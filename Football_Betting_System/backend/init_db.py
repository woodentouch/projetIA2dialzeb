"""
Script d'initialisation des données de football pour la plateforme de paris
"""
import sys
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select, SQLModel
from app import models
import os

# Récupérer l'URL de la base de données
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sports")

# Créer le moteur
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    """Initialise la base de données avec les tables"""
    SQLModel.metadata.create_all(engine)
    print("✓ Tables créées")

def seed_test_data():
    """Crée les données de test"""
    with Session(engine) as session:
        # Vérifier si les données existent déjà
        existing_events = session.exec(select(models.Event)).first()
        if existing_events:
            print("⚠ Les données de test existent déjà")
            return
        
        # Créer les événements
        events = [
            models.Event(
                team1="PSG",
                team2="Lyon",
                date=datetime.utcnow() + timedelta(days=1),
                status="active",
                odds_team1=1.45,
                odds_draw=3.8,
                odds_team2=2.7,
            ),
            models.Event(
                team1="Manchester United",
                team2="Liverpool",
                date=datetime.utcnow() + timedelta(days=2),
                status="active",
                odds_team1=2.3,
                odds_draw=3.1,
                odds_team2=1.9,
            ),
            models.Event(
                team1="Real Madrid",
                team2="Barcelona",
                date=datetime.utcnow() + timedelta(days=3),
                status="active",
                odds_team1=1.8,
                odds_draw=3.5,
                odds_team2=2.1,
            ),
        ]
        
        for event in events:
            session.add(event)
        
        session.commit()
        print(f"✓ {len(events)} événements créés")
        
        # Données des joueurs
        players_data = {
            1: [  # PSG vs Lyon
                ("PSG", "Mbappé", 7, "FW", "https://via.placeholder.com/150?text=Mbappe", 94, 38, 96, 76, 87, 89),
                ("PSG", "Neymar", 10, "FW", "https://via.placeholder.com/150?text=Neymar", 88, 39, 89, 78, 95, 81),
                ("PSG", "Marquinhos", 4, "DF", "https://via.placeholder.com/150?text=Marquinhos", 47, 88, 76, 88, 80, 85),
                ("Lyon", "Aouar", 8, "MF", "https://via.placeholder.com/150?text=Aouar", 84, 76, 83, 78, 88, 84),
                ("Lyon", "Caqueret", 6, "MF", "https://via.placeholder.com/150?text=Caqueret", 76, 73, 80, 82, 75, 83),
                ("Lyon", "Terrier", 10, "FW", "https://via.placeholder.com/150?text=Terrier", 81, 45, 86, 79, 84, 81),
            ],
            2: [  # Manchester United vs Liverpool
                ("Manchester United", "Haaland", 9, "FW", "https://via.placeholder.com/150?text=Haaland", 96, 45, 89, 93, 83, 87),
                ("Manchester United", "Rashford", 10, "FW", "https://via.placeholder.com/150?text=Rashford", 87, 48, 96, 80, 88, 89),
                ("Manchester United", "Varane", 19, "DF", "https://via.placeholder.com/150?text=Varane", 45, 89, 78, 87, 79, 82),
                ("Liverpool", "Salah", 11, "FW", "https://via.placeholder.com/150?text=Salah", 93, 45, 89, 78, 90, 87),
                ("Liverpool", "Van Dijk", 4, "DF", "https://via.placeholder.com/150?text=VanDijk", 40, 93, 79, 89, 86, 88),
                ("Liverpool", "Alisson", 1, "GK", "https://via.placeholder.com/150?text=Alisson", 38, 38, 60, 71, 85, 80),
            ],
            3: [  # Real Madrid vs Barcelona
                ("Real Madrid", "Benzema", 9, "FW", "https://via.placeholder.com/150?text=Benzema", 91, 48, 79, 81, 87, 83),
                ("Real Madrid", "Rodrygo", 11, "FW", "https://via.placeholder.com/150?text=Rodrygo", 86, 46, 91, 77, 89, 87),
                ("Real Madrid", "Nacho", 6, "DF", "https://via.placeholder.com/150?text=Nacho", 48, 84, 76, 78, 77, 85),
                ("Barcelona", "Lewandowski", 9, "FW", "https://via.placeholder.com/150?text=Lewandowski", 89, 44, 76, 82, 86, 82),
                ("Barcelona", "Gavi", 6, "MF", "https://via.placeholder.com/150?text=Gavi", 82, 79, 88, 72, 92, 84),
                ("Barcelona", "Piqué", 3, "DF", "https://via.placeholder.com/150?text=Pique", 43, 87, 67, 79, 82, 81),
            ],
        }
        
        # Créer les joueurs
        total_players = 0
        for event_id, players in players_data.items():
            for team, name, number, position, photo_url, attack, defense, speed, strength, dexterity, stamina in players:
                player = models.Player(
                    event_id=event_id,
                    team=team,
                    name=name,
                    number=number,
                    position=position,
                    photo_url=photo_url,
                    attack=attack,
                    defense=defense,
                    speed=speed,
                    strength=strength,
                    dexterity=dexterity,
                    stamina=stamina,
                )
                session.add(player)
                total_players += 1
        
        session.commit()
        print(f"✓ {total_players} joueurs créés")

def main():
    """Fonction principale"""
    try:
        print("🚀 Initialisation de la base de données de paris sportifs...")
        init_db()
        seed_test_data()
        print("\n✅ Initialisation réussie!")
        print("📊 Vous pouvez maintenant accéder à l'application")
        print("   Frontend: http://localhost:5173")
        print("   Backend: http://localhost:8000/docs")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
