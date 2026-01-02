from sqlmodel import SQLModel, Field
from typing import Optional

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: Optional[str] = None
    team1: Optional[str] = None
    team2: Optional[str] = None
    score1: Optional[int] = None
    score2: Optional[int] = None
    source: Optional[str] = None
