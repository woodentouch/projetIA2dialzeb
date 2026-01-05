"""
Routes API - Simplifiées
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select, create_engine
from datetime import datetime
import os

from . import models

router = APIRouter(prefix="/api", tags=["betting"])

# DB Engine
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sports")
engine = create_engine(DATABASE_URL)

class BetRequest(BaseModel):
    event_id: int
    bet_type: str
    amount: float
    odds: float
    user_id: int = 1


@router.get("/events")
def get_events():
    """Récupère tous les événements de football"""
    with Session(engine) as session:
        events = session.exec(select(models.Event)).all()
        return {"events": [{
            "id": e.id, 
            "team1": e.team1, 
            "team2": e.team2,
            "date": e.date.isoformat() if e.date else None,
            "status": e.status,
            "odds_team1": e.odds_team1,
            "odds_draw": e.odds_draw,
            "odds_team2": e.odds_team2,
            "result": e.result
        } for e in events]}


@router.post("/bets")
def place_bet(bet_request: BetRequest):
    """Place a bet on an event"""
    with Session(engine) as session:
        # Verify event exists
        event = session.exec(select(models.Event).where(models.Event.id == bet_request.event_id)).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Create bet
        bet = models.Bet(
            event_id=bet_request.event_id,
            user_id=bet_request.user_id,
            bet_type=bet_request.bet_type,
            amount=bet_request.amount,
            odds=bet_request.odds,
            status="pending",
            created_at=datetime.utcnow()
        )
        session.add(bet)
        session.commit()
        session.refresh(bet)
        
        return {
            "status": "ok",
            "bet_id": bet.id,
            "event_id": bet.event_id,
            "bet_type": bet.bet_type,
            "amount": bet.amount,
            "odds": bet.odds,
            "potential_win": bet.amount * bet.odds
        }


@router.get("/my-bets")
def get_my_bets(user_id: int = 1):
    """Get user bets with event details"""
    with Session(engine) as session:
        bets = session.exec(
            select(models.Bet).where(models.Bet.user_id == user_id)
        ).all()
        
        bets_data = []
        for bet in bets:
            event = session.exec(
                select(models.Event).where(models.Event.id == bet.event_id)
            ).first()
            
            bets_data.append({
                "id": bet.id,
                "event_id": bet.event_id,
                "event": f"{event.team1} vs {event.team2}" if event else "Unknown",
                "bet_type": bet.bet_type,
                "amount": bet.amount,
                "odds": bet.odds,
                "status": bet.status,
                "created_at": bet.created_at.isoformat() if bet.created_at else None
            })
        
        return {"bets": bets_data}


@router.post("/seed-data")
def seed_data():
    """Create comprehensive test data with historical matches and realistic player stats"""
    from datetime import datetime, timedelta
    import random
    
    with Session(engine) as session:
        # Check if data already exists
        existing = session.exec(select(models.Event)).first()
        if existing:
            return {
                "message": "Data already exists. Use /api/reset-data to clear first.",
                "existing_events": session.exec(select(models.Event)).all()
            }
        
        # Create comprehensive historical match data (last 6 months)
        historical_matches = [
            # PSG matches
            ("PSG", "Lyon", 3, 1, 180),
            ("PSG", "Marseille", 2, 1, 150),
            ("PSG", "Monaco", 4, 2, 120),
            ("Lyon", "PSG", 1, 2, 90),
            ("PSG", "Nice", 3, 0, 60),
            ("PSG", "Lille", 2, 2, 30),
            
            # Manchester United matches
            ("Manchester United", "Liverpool", 2, 1, 175),
            ("Manchester United", "Chelsea", 1, 1, 145),
            ("Liverpool", "Manchester United", 3, 2, 115),
            ("Manchester United", "Arsenal", 3, 1, 85),
            ("Manchester United", "Tottenham", 2, 0, 55),
            ("Manchester United", "Manchester City", 1, 2, 25),
            
            # Real Madrid matches
            ("Real Madrid", "Barcelona", 2, 1, 170),
            ("Real Madrid", "Atletico Madrid", 3, 1, 140),
            ("Barcelona", "Real Madrid", 1, 2, 110),
            ("Real Madrid", "Sevilla", 4, 1, 80),
            ("Real Madrid", "Valencia", 2, 0, 50),
            ("Real Madrid", "Athletic Bilbao", 3, 2, 20),
            
            # Liverpool matches
            ("Liverpool", "Chelsea", 2, 0, 165),
            ("Liverpool", "Arsenal", 3, 1, 135),
            ("Liverpool", "Tottenham", 2, 2, 105),
            ("Chelsea", "Liverpool", 1, 1, 75),
            ("Liverpool", "Leicester", 3, 0, 45),
            
            # Barcelona matches
            ("Barcelona", "Atletico Madrid", 2, 1, 160),
            ("Barcelona", "Sevilla", 3, 0, 130),
            ("Atletico Madrid", "Barcelona", 1, 1, 100),
            ("Barcelona", "Valencia", 4, 2, 70),
            ("Barcelona", "Real Sociedad", 2, 1, 40),
            
            # Additional cross-league matches for diversity
            ("Bayern Munich", "Borussia Dortmund", 3, 2, 155),
            ("Inter Milan", "AC Milan", 2, 1, 125),
            ("Arsenal", "Chelsea", 2, 2, 95),
            ("Atletico Madrid", "Sevilla", 1, 0, 65),
            ("Manchester City", "Liverpool", 1, 1, 35),
        ]
        
        # Insert historical matches
        for team1, team2, score1, score2, days_ago in historical_matches:
            match = models.Match(
                team1=team1,
                team2=team2,
                score1=score1,
                score2=score2,
                date=(datetime.utcnow() - timedelta(days=days_ago)).isoformat(),
                source="seed_data"
            )
            session.add(match)
        
        session.commit()
        
        # Create upcoming events with realistic odds
        events_data = [
            {
                "team1": "PSG", "team2": "Lyon",
                "date": datetime.utcnow() + timedelta(days=1, hours=19),
                "odds_team1": 1.65, "odds_draw": 3.8, "odds_team2": 4.5
            },
            {
                "team1": "Manchester United", "team2": "Liverpool",
                "date": datetime.utcnow() + timedelta(days=2, hours=18, minutes=30),
                "odds_team1": 2.3, "odds_draw": 3.4, "odds_team2": 2.9
            },
            {
                "team1": "Real Madrid", "team2": "Barcelona",
                "date": datetime.utcnow() + timedelta(days=3, hours=21),
                "odds_team1": 2.1, "odds_draw": 3.5, "odds_team2": 3.2
            },
            {
                "team1": "Bayern Munich", "team2": "Borussia Dortmund",
                "date": datetime.utcnow() + timedelta(days=4, hours=17, minutes=30),
                "odds_team1": 1.75, "odds_draw": 3.9, "odds_team2": 4.2
            },
            {
                "team1": "Arsenal", "team2": "Chelsea",
                "date": datetime.utcnow() + timedelta(days=5, hours=20),
                "odds_team1": 2.4, "odds_draw": 3.3, "odds_team2": 2.8
            },
        ]
        
        for event_data in events_data:
            event = models.Event(
                team1=event_data["team1"],
                team2=event_data["team2"],
                date=event_data["date"],
                status="active",
                odds_team1=event_data["odds_team1"],
                odds_draw=event_data["odds_draw"],
                odds_team2=event_data["odds_team2"]
            )
            session.add(event)
        
        session.commit()
        
        # Create realistic player data
        player_templates = {
            "PSG": [
                ("Kylian Mbappé", 7, "FW", 95, 45, 97, 85, 92, 88),
                ("Neymar Jr", 10, "FW", 93, 38, 87, 68, 95, 82),
                ("Marco Verratti", 6, "MF", 72, 85, 78, 70, 88, 86),
                ("Marquinhos", 5, "DF", 45, 92, 82, 88, 85, 84),
                ("Gianluigi Donnarumma", 99, "GK", 20, 95, 68, 85, 90, 80),
                ("Achraf Hakimi", 2, "DF", 78, 83, 94, 82, 88, 90),
            ],
            "Lyon": [
                ("Alexandre Lacazette", 9, "FW", 88, 42, 78, 80, 84, 82),
                ("Corentin Tolisso", 8, "MF", 75, 78, 76, 82, 80, 85),
                ("Castello Lukeba", 4, "DF", 40, 84, 80, 86, 78, 82),
                ("Anthony Lopes", 1, "GK", 18, 88, 65, 80, 86, 78),
                ("Nicolás Tagliafico", 3, "DF", 55, 82, 78, 84, 80, 84),
                ("Rayan Cherki", 18, "MF", 82, 55, 85, 65, 90, 75),
            ],
            "Manchester United": [
                ("Marcus Rashford", 10, "FW", 90, 48, 93, 78, 86, 88),
                ("Bruno Fernandes", 8, "MF", 85, 68, 74, 72, 90, 86),
                ("Raphaël Varane", 19, "DF", 38, 90, 78, 88, 82, 84),
                ("David de Gea", 1, "GK", 15, 92, 62, 78, 88, 82),
                ("Casemiro", 18, "MF", 58, 88, 68, 90, 78, 88),
                ("Luke Shaw", 23, "DF", 62, 84, 76, 82, 80, 84),
            ],
            "Liverpool": [
                ("Mohamed Salah", 11, "FW", 94, 45, 90, 75, 92, 86),
                ("Darwin Núñez", 27, "FW", 89, 40, 88, 86, 78, 84),
                ("Virgil van Dijk", 4, "DF", 48, 93, 75, 92, 80, 86),
                ("Alisson Becker", 1, "GK", 22, 94, 68, 84, 90, 82),
                ("Trent Alexander-Arnold", 66, "DF", 75, 80, 82, 74, 92, 86),
                ("Fabinho", 3, "MF", 55, 90, 70, 86, 82, 88),
            ],
            "Real Madrid": [
                ("Karim Benzema", 9, "FW", 92, 48, 78, 82, 90, 80),
                ("Vinícius Júnior", 20, "FW", 91, 42, 95, 78, 88, 86),
                ("Luka Modrić", 10, "MF", 75, 80, 76, 68, 92, 78),
                ("Thibaut Courtois", 1, "GK", 18, 92, 60, 88, 85, 80),
                ("David Alaba", 4, "DF", 52, 88, 78, 84, 86, 84),
                ("Toni Kroos", 8, "MF", 72, 78, 68, 74, 94, 76),
            ],
            "Barcelona": [
                ("Robert Lewandowski", 9, "FW", 94, 45, 78, 86, 88, 82),
                ("Pedri", 8, "MF", 78, 72, 80, 68, 90, 85),
                ("Gavi", 6, "MF", 75, 76, 84, 74, 88, 90),
                ("Marc-André ter Stegen", 1, "GK", 20, 91, 65, 82, 88, 80),
                ("Ronald Araújo", 4, "DF", 45, 90, 82, 92, 76, 88),
                ("Frenkie de Jong", 21, "MF", 70, 82, 78, 80, 88, 86),
            ],
            "Bayern Munich": [
                ("Thomas Müller", 25, "FW", 86, 58, 72, 76, 90, 82),
                ("Sadio Mané", 17, "FW", 90, 48, 91, 80, 86, 88),
                ("Joshua Kimmich", 6, "MF", 68, 86, 74, 78, 90, 88),
                ("Manuel Neuer", 1, "GK", 18, 93, 62, 84, 88, 80),
                ("Matthijs de Ligt", 4, "DF", 42, 88, 76, 90, 80, 84),
                ("Alphonso Davies", 19, "DF", 68, 82, 96, 78, 82, 92),
            ],
            "Borussia Dortmund": [
                ("Karim Adeyemi", 27, "FW", 84, 40, 94, 72, 82, 86),
                ("Marco Reus", 11, "MF", 86, 62, 78, 70, 90, 76),
                ("Jude Bellingham", 22, "MF", 78, 76, 82, 80, 86, 88),
                ("Gregor Kobel", 1, "GK", 16, 86, 64, 80, 82, 78),
                ("Niklas Süle", 25, "DF", 48, 86, 68, 88, 74, 80),
                ("Mats Hummels", 15, "DF", 45, 88, 62, 86, 82, 76),
            ],
            "Arsenal": [
                ("Bukayo Saka", 7, "FW", 88, 52, 89, 72, 88, 86),
                ("Martin Ødegaard", 8, "MF", 82, 68, 76, 68, 92, 84),
                ("Gabriel Jesus", 9, "FW", 89, 48, 86, 78, 88, 88),
                ("Aaron Ramsdale", 1, "GK", 18, 84, 66, 76, 80, 80),
                ("William Saliba", 12, "DF", 42, 86, 82, 84, 78, 86),
                ("Thomas Partey", 5, "MF", 65, 84, 74, 82, 80, 86),
            ],
            "Chelsea": [
                ("Raheem Sterling", 17, "FW", 87, 45, 90, 72, 86, 84),
                ("Mason Mount", 19, "MF", 80, 70, 78, 72, 88, 86),
                ("Enzo Fernández", 5, "MF", 75, 78, 76, 76, 88, 84),
                ("Kepa Arrizabalaga", 1, "GK", 16, 84, 64, 78, 82, 78),
                ("Thiago Silva", 6, "DF", 40, 92, 58, 78, 88, 70),
                ("Reece James", 24, "DF", 72, 84, 86, 82, 84, 88),
            ],
        }
        
        # Add players for each event
        for event in session.exec(select(models.Event)).all():
            team1_players = player_templates.get(event.team1, [])
            team2_players = player_templates.get(event.team2, [])
            
            for name, number, position, attack, defense, speed, strength, dexterity, stamina in team1_players:
                player = models.Player(
                    event_id=event.id,
                    team=event.team1,
                    name=name,
                    number=number,
                    position=position,
                    photo_url=f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=200&background=random",
                    attack=attack,
                    defense=defense,
                    speed=speed,
                    strength=strength,
                    dexterity=dexterity,
                    stamina=stamina
                )
                session.add(player)
            
            for name, number, position, attack, defense, speed, strength, dexterity, stamina in team2_players:
                player = models.Player(
                    event_id=event.id,
                    team=event.team2,
                    name=name,
                    number=number,
                    position=position,
                    photo_url=f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=200&background=random",
                    attack=attack,
                    defense=defense,
                    speed=speed,
                    strength=strength,
                    dexterity=dexterity,
                    stamina=stamina
                )
                session.add(player)
        
        session.commit()
        
        # Get counts for summary
        event_count = len(session.exec(select(models.Event)).all())
        player_count = len(session.exec(select(models.Player)).all())
        match_count = len(session.exec(select(models.Match)).all())
        
        return {
            "message": "Comprehensive data seeded successfully!",
            "events_created": event_count,
            "historical_matches": match_count,
            "players_created": player_count,
            "teams": list(set([e.team1 for e in session.exec(select(models.Event)).all()] + 
                             [e.team2 for e in session.exec(select(models.Event)).all()]))
        }


@router.post("/reset-data")
def reset_data():
    """Delete all data (events, players, bets, matches) - USE WITH CAUTION"""
    with Session(engine) as session:
        # Delete in correct order due to foreign keys
        session.exec(select(models.Bet)).all()
        for bet in session.exec(select(models.Bet)).all():
            session.delete(bet)
        
        for player in session.exec(select(models.Player)).all():
            session.delete(player)
        
        for event in session.exec(select(models.Event)).all():
            session.delete(event)
        
        for match in session.exec(select(models.Match)).all():
            session.delete(match)
        
        session.commit()
        
        return {
            "message": "All data cleared successfully",
            "status": "reset_complete"
        }

