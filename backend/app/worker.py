import os
import json
import requests
from redis import Redis
from sqlmodel import create_engine, Session
from .models import Team, Match
from .crud import insert_match

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")
redis_conn = Redis.from_url(REDIS_URL)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sports")
engine = create_engine(DATABASE_URL)

# Small helper to wait for DB readiness when running directly (useful for local tests)
import time
import logging
logger = logging.getLogger("worker")

def wait_for_db(engine, retries: int = 10, delay: float = 1.0, backoff: float = 1.5):
    attempt = 0
    curr_delay = delay
    while attempt < retries:
        try:
            with engine.connect() as conn:
                # Use exec_driver_sql for compatibility across SQLAlchemy versions
                conn.exec_driver_sql("SELECT 1")
            logger.info("Worker connected to DB")
            return
        except Exception as e:
            attempt += 1
            logger.warning(f"Worker waiting for DB (attempt {attempt}/{retries}): {e}")
            time.sleep(curr_delay)
            curr_delay *= backoff
    raise RuntimeError("Worker could not connect to DB after retries")

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def scrape_matches():
    """Scrape a public football dataset as an example and save to data/matches.json.
    In addition to saving the raw JSON, normalize and insert matches into the Postgres DB.
    """
    print("Starting scrape_matches job...")
    # Example public dataset (openfootball)
    url = "https://raw.githubusercontent.com/openfootball/football.json/master/2019-20/en.1.json"
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
        # Keep only rounds/matches for simplicity
        matches = []
        rounds = payload.get("rounds", [])
        for r in rounds:
            for m in r.get("matches", []):
                matches.append({
                    "date": m.get("date"),
                    "team1": m.get("team1"),
                    "team2": m.get("team2"),
                    "score1": m.get("score1"),
                    "score2": m.get("score2"),
                })
        out = {"source": url, "count": len(matches), "matches": matches}
        with open(os.path.join(DATA_DIR, "matches.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"Scraped {len(matches)} matches and saved to data/matches.json")

        # Insert into DB (normalize and upsert teams)
        inserted = 0
        with Session(engine) as session:
            for m in matches:
                try:
                    insert_match(session, {**m, "source": url})
                    inserted += 1
                except Exception as e:
                    print("Insert failed for match", m, str(e))
        print(f"Inserted {inserted} matches into the DB")
        return out
    except Exception as e:
        print("Scrape failed:", e)
        # Fallback: create a tiny sample
        sample = {"source": "sample", "count": 1, "matches": [{"date": "2020-01-01", "team1": "Home", "team2": "Away", "score1": 1, "score2": 0}]}
        with open(os.path.join(DATA_DIR, "matches.json"), "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        # also insert sample into DB
        with Session(engine) as session:
            insert_match(session, {**sample['matches'][0], "source": "sample"})
        return sample


from rq import get_current_job
import uuid
import pymc as pm
import arviz as az
import numpy as np


def run_inference(method: str = 'advi', mcmc_draws: int = 1000, mcmc_tune: int = 1000):
    """Run a Bayesian Poisson hierarchical model on matches in the DB and save posterior summaries to a JSON file.
    Supports 'advi' (fast) and 'mcmc' (more accurate but slower). Works with RQ (args passed when enqueuing).
    """
    job = get_current_job()
    jid = job.get_id() if job else str(uuid.uuid4())
    print(f"Starting inference job {jid} (method={method}, draws={mcmc_draws}, tune={mcmc_tune})")

    # Load matches from DB
    from sqlmodel import Session, select
    with Session(engine) as session:
        stmt = select(Match).where(Match.score1 != None, Match.score2 != None)
        rows = session.exec(stmt).all()

    # Prepare data
    teams = {}
    home = []
    away = []
    ghome = []
    gaway = []
    for r in rows:
        if r.team1 is None or r.team2 is None:
            continue
        for t in (r.team1, r.team2):
            if t not in teams:
                teams[t] = len(teams)
        home.append(teams[r.team1])
        away.append(teams[r.team2])
        ghome.append(0 if r.score1 is None else r.score1)
        gaway.append(0 if r.score2 is None else r.score2)

    if len(home) == 0 or len(teams) == 0:
        result = {"error": "Not enough data for inference"}
        out_path = os.path.join(DATA_DIR, f"inference_{jid}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return result

    home = np.array(home)
    away = np.array(away)
    ghome = np.array(ghome)
    gaway = np.array(gaway)
    n_teams = len(teams)

    with pm.Model() as model:
        mu = pm.Normal("mu", mu=0.0, sigma=1.0)
        home_adv = pm.Normal("home_adv", mu=0.0, sigma=0.5)
        attack = pm.Normal("attack", mu=0.0, sigma=1.0, shape=n_teams)
        defense = pm.Normal("defense", mu=0.0, sigma=1.0, shape=n_teams)

        theta_home = pm.math.exp(mu + home_adv + attack[home] + defense[away])
        theta_away = pm.math.exp(mu + attack[away] + defense[home])

        obs_home = pm.Poisson("obs_home", mu=theta_home, observed=ghome)
        obs_away = pm.Poisson("obs_away", mu=theta_away, observed=gaway)

        if method == 'mcmc':
            # Use MCMC sampling (more accurate but slower)
            idata = pm.sample(draws=mcmc_draws, tune=mcmc_tune, chains=2, cores=1, progressbar=False, return_inferencedata=True)
            trace = None
        else:
            # Default to ADVI for quick demo
            approx = pm.fit(n=4000, method="advi", progressbar=False)
            trace = approx.sample(draws=1000)
            try:
                idata = az.from_pymc3(trace=trace, model=model)
            except Exception:
                idata = az.from_dict(posterior={k: np.array(v) for k, v in trace.items()})

    # Summarize with ArviZ
    summary = az.summary(idata).to_dict()

    # Compute diagnostics (R_hat, ESS) and convert to JSON-serializable python types
    try:
        rhat_raw = az.rhat(idata).to_dict()
    except Exception:
        rhat_raw = {}
    try:
        ess_raw = az.ess(idata).to_dict()
    except Exception:
        ess_raw = {}

    def _np_to_py(o):
        if isinstance(o, dict):
            return {k: _np_to_py(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_np_to_py(v) for v in o]
        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        return o

    rhat = _np_to_py(rhat_raw)
    ess = _np_to_py(ess_raw)

    # Map attack means back to team names
    attack_means = {}
    if method == 'mcmc':
        # extract posterior arrays from idata (xarray)
        try:
            attack_vals = idata.posterior['attack'].values  # shape (chains, draws, n_teams)
            # merge chains and draws
            attack_vals = attack_vals.reshape(-1, attack_vals.shape[-1])
            means = attack_vals.mean(axis=0).tolist()
        except Exception:
            means = []
    else:
        if trace and "attack" in trace:
            attack_vals = np.array(trace["attack"])  # shape (draws, n_teams)
            means = attack_vals.mean(axis=0).tolist()
        else:
            means = []

    inv = {idx: name for name, idx in teams.items()}
    for i, m in enumerate(means):
        attack_means[inv[i]] = m

    # Export posterior samples (truncated to reasonable size for JSON)
    posteriors = {}
    # collect samples depending on method
    max_samples = 500
    if method == 'mcmc':
        try:
            # idata.posterior is xarray with dims (chain, draw, ...)
            def flatten_arr(x):
                arr = x.values.reshape(-1, *x.shape[2:]) if x.ndim >= 3 else x.values.reshape(-1)
                return arr
            if 'mu' in idata.posterior:
                mu_arr = flatten_arr(idata.posterior['mu'])
                posteriors['mu'] = mu_arr[:max_samples].tolist()
            if 'home_adv' in idata.posterior:
                ha_arr = flatten_arr(idata.posterior['home_adv'])
                posteriors['home_adv'] = ha_arr[:max_samples].tolist()
            if 'attack' in idata.posterior:
                attack_arr = idata.posterior['attack'].values.reshape(-1, idata.posterior['attack'].shape[-1])
                attack_samples = {}
                for i in range(attack_arr.shape[1]):
                    attack_samples[inv[i]] = attack_arr[:, i][:max_samples].tolist()
                posteriors['attack'] = attack_samples
        except Exception:
            pass
    else:
        # ADVI (trace is a dict)
        num_draws = None
        for k, v in (trace or {}).items():
            try:
                arr = np.array(v)
                if arr.ndim >= 1:
                    num_draws = arr.shape[0]
                    break
            except Exception:
                continue
        max_samples = min(num_draws or 0, 500)
        if max_samples > 0:
            if "mu" in trace:
                posteriors["mu"] = np.array(trace["mu"])[:max_samples].tolist()
            if "home_adv" in trace:
                posteriors["home_adv"] = np.array(trace["home_adv"])[:max_samples].tolist()
            if "attack" in trace:
                attack_arr = np.array(trace["attack"])[:max_samples]  # shape (samples, n_teams)
                attack_samples = {}
                for i in range(attack_arr.shape[1]):
                    attack_samples[inv[i]] = attack_arr[:, i].tolist()
                posteriors["attack"] = attack_samples

    out = {
        "job_id": jid,
        "n_matches": len(home),
        "n_teams": n_teams,
        "attack_means": attack_means,
        "summary_stats": summary,
        "posteriors": posteriors,
        "teams": list(teams.keys()),
        "diagnostics": {"rhat": rhat, "ess": ess},
        "method": method,
    }

    out_path = os.path.join(DATA_DIR, f"inference_{jid}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Inference job {jid} finished, results saved to {out_path}")
    return out


# If this file is executed directly (worker container can run `python -u app/worker.py` to test)
if __name__ == "__main__":
    print("Running scrape_matches directly for quick test")
    try:
        wait_for_db(engine)
    except Exception as e:
        print("DB not available, exiting:", e)
        raise
    scrape_matches()
