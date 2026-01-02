import os
import json
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from rq import Queue
from sqlmodel import SQLModel, create_engine, Session
from . import models
import time
import logging
from sqlalchemy.exc import OperationalError

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Bayesian Sports Analytics - Backend")


def wait_for_db(engine, retries: int = 10, delay: float = 1.0, backoff: float = 1.5):
    """Wait for the database to become available, with exponential backoff.
    Raises RuntimeError if the DB is not reachable after retries.
    """
    attempt = 0
    curr_delay = delay
    while attempt < retries:
        try:
            # try a simple connect and a lightweight statement
            with engine.connect() as conn:
                # Use exec_driver_sql to execute a raw SQL string across SQLAlchemy versions
                conn.exec_driver_sql("SELECT 1")
            # If connect succeeded, create tables and return
            SQLModel.metadata.create_all(engine)
            logger.info("Connected to DB and ensured tables exist")
            return
        except Exception as e:
            attempt += 1
            logger.warning(f"Database not ready (attempt {attempt}/{retries}): {e}")
            time.sleep(curr_delay)
            curr_delay *= backoff
    raise RuntimeError("Could not connect to the database after retries")

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis / RQ
redis_url = os.environ.get("REDIS_URL", "redis://redis:6379")
redis_conn = Redis.from_url(redis_url)
q = Queue(connection=redis_conn)

# DB
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sports")
engine = create_engine(DATABASE_URL)

@app.on_event("startup")
def on_startup():
    # Wait for DB to be ready and create tables (retries configurable via env)
    retries = int(os.environ.get("DB_STARTUP_RETRIES", "12"))
    delay = float(os.environ.get("DB_STARTUP_DELAY", "1.0"))
    backoff = float(os.environ.get("DB_STARTUP_BACKOFF", "1.6"))
    try:
        wait_for_db(engine, retries=retries, delay=delay, backoff=backoff)
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Re-raise so the failure is visible and the container exits (Compose restart may kick in)
        raise

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/scrape")
def enqueue_scrape(background_tasks: BackgroundTasks):
    job = q.enqueue("app.worker.scrape_matches")
    return {"job_id": job.get_id(), "status": "queued"}

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    from rq.job import Job
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {"id": job.get_id(), "status": job.get_status(), "result": job.result}
    except Exception as e:
        return {"error": str(e)}

@app.post('/api/infer')
def enqueue_inference(method: str = 'advi', draws: int = 1000, tune: int = 1000):
    """Enqueue an inference job.
    - method: 'advi' (fast) or 'mcmc' (more accurate, slower)
    - draws/tune only used for MCMC (pm.sample)
    """
    job = q.enqueue("app.worker.run_inference", method=method, mcmc_draws=draws, mcmc_tune=tune)
    return {"job_id": job.get_id(), "status": "queued", "method": method, "draws": draws, "tune": tune}

@app.get('/api/infer/results/{job_id}')
def get_inference_result(job_id: str):
    path = os.path.join(os.getcwd(), "data", f"inference_{job_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "result not ready"}

@app.get("/api/data/matches")
def list_matches_file():
    # Return the scraped matches JSON if present
    path = os.path.join(os.getcwd(), "data", "matches.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"matches": []}

@app.get("/api/db/matches")
def list_matches_db(team: str = None, limit: int = 100, offset: int = 0):
    """List matches from the Postgres DB with optional filtering by team."""
    with Session(engine) as session:
        from .crud import list_matches
        rows = list_matches(session, team=team, limit=limit, offset=offset)
        return {"count": len(rows), "matches": [r.dict() for r in rows]}

@app.get("/api/db/teams")
def list_teams_db():
    """List teams in DB"""
    with Session(engine) as session:
        from .crud import list_teams
        rows = list_teams(session)
        return {"count": len(rows), "teams": [r.dict() for r in rows]}
