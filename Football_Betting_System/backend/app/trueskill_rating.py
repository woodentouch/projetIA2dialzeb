from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, Dict

from trueskill import TrueSkill, Rating


# Soccer has a relatively high draw rate; set draw_probability accordingly.
# This value is a modeling choice; tweak if you have league-specific stats.
TRUESKILL_ENV = TrueSkill(draw_probability=0.26)


@dataclass(frozen=True)
class TeamSkill:
    team: str
    mu: float
    sigma: float


def default_rating() -> Rating:
    return TRUESKILL_ENV.create_rating()


def to_rating(mu: float, sigma: float) -> Rating:
    return Rating(mu=mu, sigma=sigma)


def expected_outcome_probabilities(team1: TeamSkill, team2: TeamSkill) -> Dict[str, float]:
    """Return win/draw/loss probabilities based on the TrueSkill model assumptions.

    Uses the standard Gaussian approximation with draw margin derived from draw_probability.
    """
    import math
    from scipy.stats import norm
    
    r1 = to_rating(team1.mu, team1.sigma)
    r2 = to_rating(team2.mu, team2.sigma)

    # c^2 = 2*beta^2 + sigma1^2 + sigma2^2
    beta = TRUESKILL_ENV.beta
    c = math.sqrt(2 * (beta ** 2) + (r1.sigma ** 2) + (r2.sigma ** 2))

    delta_mu = r1.mu - r2.mu
    
    # Calculate draw_margin from draw_probability
    # draw_margin ≈ -epsilon * c * sqrt(2), where epsilon = norm.ppf((1-p_draw)/2)
    # For simplicity, use a heuristic based on beta and draw_probability
    draw_margin = math.sqrt(2) * beta * norm.ppf((1 + TRUESKILL_ENV.draw_probability) / 2)

    # Standard normal CDF
    p_team1_win = 1.0 - norm.cdf((draw_margin - delta_mu) / c)
    p_draw = norm.cdf((draw_margin - delta_mu) / c) - norm.cdf((-draw_margin - delta_mu) / c)
    p_team2_win = norm.cdf((-draw_margin - delta_mu) / c)

    # Guard against small numerical drift
    total = p_team1_win + p_draw + p_team2_win
    if total > 0:
        p_team1_win /= total
        p_draw /= total
        p_team2_win /= total

    return {
        "team1_win": float(p_team1_win),
        "draw": float(p_draw),
        "team2_win": float(p_team2_win),
    }


def update_ratings_after_match(
    team1: TeamSkill,
    team2: TeamSkill,
    score1: int,
    score2: int,
) -> Tuple[TeamSkill, TeamSkill, str]:
    """Update two team ratings after a match.

    Returns updated skills + normalized result string: team1|team2|draw
    """
    r1 = to_rating(team1.mu, team1.sigma)
    r2 = to_rating(team2.mu, team2.sigma)

    if score1 == score2:
        (nr1, nr2) = TRUESKILL_ENV.rate_1vs1(r1, r2, drawn=True)
        result = "draw"
    elif score1 > score2:
        (nr1, nr2) = TRUESKILL_ENV.rate_1vs1(r1, r2)
        result = "team1"
    else:
        # team2 wins
        (nr2, nr1) = TRUESKILL_ENV.rate_1vs1(r2, r1)
        result = "team2"

    return (
        TeamSkill(team=team1.team, mu=float(nr1.mu), sigma=float(nr1.sigma)),
        TeamSkill(team=team2.team, mu=float(nr2.mu), sigma=float(nr2.sigma)),
        result,
    )
