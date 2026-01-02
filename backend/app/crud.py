from typing import Optional, List
from sqlmodel import Session, select
from .models import Team, Match


def get_or_create_team(session: Session, name: str) -> Team:
    name_clean = (name or "").strip()
    if not name_clean:
        raise ValueError("Empty team name")
    stmt = select(Team).where(Team.name == name_clean)
    res = session.exec(stmt).first()
    if res:
        return res
    team = Team(name=name_clean)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


def insert_match(session: Session, m: dict) -> Match:
    # m expected keys: date, team1, team2, score1, score2, source
    t1 = get_or_create_team(session, m.get("team1") or "")
    t2 = get_or_create_team(session, m.get("team2") or "")
    match = Match(
        date=m.get("date"),
        team1=t1.name,
        team2=t2.name,
        score1=(m.get("score1") if m.get("score1") is not None else None),
        score2=(m.get("score2") if m.get("score2") is not None else None),
        source=m.get("source")
    )
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def list_matches(session: Session, team: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Match]:
    stmt = select(Match)
    if team:
        stmt = stmt.where((Match.team1 == team) | (Match.team2 == team))
    stmt = stmt.limit(limit).offset(offset)
    return session.exec(stmt).all()


def list_teams(session: Session) -> List[Team]:
    stmt = select(Team)
    return session.exec(stmt).all()
