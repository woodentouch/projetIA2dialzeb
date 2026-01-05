# 🎯 Football Betting Platform

Une plateforme moderne de paris sur des événements de football avec gestion des joueurs, affichage de leurs critères de jeu (style FIFA), et historique des paris.

## 🎮 Caractéristiques

### Frontend
- ⚽ **Gestion des Événements**: Consulter tous les événements de football disponibles
- 💰 **Système de Paris**: Parier sur le résultat des matchs (victoire équipe 1, match nul, victoire équipe 2)
- 🏃 **Affichage des Joueurs**: Voir tous les joueurs avec leurs photos et statistiques
- 📊 **Critères FIFA**: Chaque joueur a 6 critères (Attaque, Défense, Vitesse, Force, Dextérité, Endurance) notés de 0-100
- 📈 **Historique des Paris**: Suivre tous vos paris, leur statut et vos gains potentiels
- 🎨 **Interface Moderne**: Design responsive et intuitif avec Mantine UI

### Backend
- 📱 **API REST** complète avec FastAPI
- 🗄️ **Base de données PostgreSQL** pour la persistance
- 🔄 **Gestion des événements et joueurs**
- 💳 **Système complet de paris** avec statuts et cotes

## 📦 Installation

### Prérequis
- Docker et Docker Compose
- Node.js 18+ (pour développement local du frontend)
- Python 3.9+ (pour développement local du backend)

### Configuration avec Docker Compose

```bash
# Cloner le projet
cd c:\Users\alifa\Desktop\projetIA2dialzeb

# Démarrer tous les services
docker-compose up -d

# Accéder à l'application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Configuration Locale

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Accès: http://localhost:5173
```

#### Backend
```bash
cd backend
pip install -r requirements.txt

# Configurer les variables d'environnement
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sports
# REDIS_URL=redis://localhost:6379

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Accès: http://localhost:8000
```

## 🚀 Utilisation

### 1. Initialiser les données de test

```bash
# Appeler le endpoint de seed une fois
curl -X POST http://localhost:8000/api/seed-data
```

Cela crée automatiquement:
- 3 événements de football (PSG vs Lyon, Manchester vs Liverpool, Real vs Barcelona)
- 18 joueurs au total avec photos et critères FIFA

### 2. Naviguer sur la plateforme

#### Tab 1: Événements
- Affiche tous les événements de football disponibles
- Voir les cotes pour chaque résultat possible
- Date et heure de l'événement

#### Tab 2: Parier
- Sélectionner un événement à gauche
- Voir les cotes mises à jour
- Consulter la liste des joueurs avec:
  - Photo du joueur
  - Numéro et position
  - 6 critères de jeu (0-100)
- Cliquer sur "Parier" pour placer un pari
- Montant minimum: 0€ (configurable)

#### Tab 3: Mes Paris
- Historique complet de tous vos paris
- Statistiques de paris:
  - Total misé
  - Gains potentiels
  - Nombre de paris
  - Taux de réussite
- Voir le détail de chaque pari
- Statuts des paris: En attente, Gagné, Perdu, Annulé

## 📊 Structure de la Base de Données

### Event
```python
- id: Identifiant unique
- team1: Nom de la première équipe
- team2: Nom de la deuxième équipe
- date: Date et heure de l'événement
- status: active, finished, cancelled
- odds_team1: Cote pour la victoire de team1
- odds_draw: Cote pour le match nul
- odds_team2: Cote pour la victoire de team2
- result: team1, draw, ou team2 (après le match)
```

### Player
```python
- id: Identifiant unique
- event_id: Lien vers l'événement
- team: Équipe du joueur
- name: Nom du joueur
- number: Numéro du maillot
- position: GK (gardien), DF (défenseur), MF (milieu), FW (attaquant)
- photo_url: URL de la photo
- attack: Attaque (0-100)
- defense: Défense (0-100)
- speed: Vitesse (0-100)
- strength: Force (0-100)
- dexterity: Dextérité (0-100)
- stamina: Endurance (0-100)
```

### Bet
```python
- id: Identifiant unique
- event_id: Lien vers l'événement
- user_id: ID de l'utilisateur
- bet_type: team1, draw, team2, etc.
- amount: Montant du pari
- odds: Cote au moment du pari
- status: pending, won, lost, cancelled
- created_at: Timestamp de création
- result_at: Timestamp du résultat
```

## 🔌 API Endpoints

### Événements
```
GET /api/events                      # Tous les événements
GET /api/events/{event_id}           # Détails d'un événement
GET /api/events/{event_id}/players   # Joueurs d'un événement
```

### Paris
```
POST /api/bets                       # Placer un nouveau pari
GET /api/my-bets?user_id=1          # Mes paris
GET /api/bets/{bet_id}              # Détails d'un pari
```

### Données de test
```
POST /api/seed-data                 # Créer les données de démo
```

## 🛠️ Technologies

### Frontend
- **React 18**: Framework UI
- **Vite**: Bundler moderne
- **Mantine UI 7**: Composants d'interface
- **Axios**: Client HTTP
- **Recharts**: Graphiques (optionnel)

### Backend
- **FastAPI**: Framework web Python
- **SQLModel**: ORM avec SQLAlchemy
- **PostgreSQL**: Base de données
- **Redis**: Cache et queuing (optionnel)
- **RQ**: Task queue (optionnel)

## 📝 Fichiers Principaux

```
frontend/
├── src/
│   ├── App.jsx                  # Composant principal avec tabs
│   ├── components/
│   │   ├── EventsList.jsx       # Liste des événements
│   │   ├── BettingDashboard.jsx # Interface de paris
│   │   └── MyBets.jsx           # Historique des paris
│   └── styles.css               # Styles globaux
│
backend/
├── app/
│   ├── main.py                  # Application FastAPI principale
│   ├── models.py                # Modèles SQLModel (Event, Player, Bet)
│   ├── betting_routes.py        # Routes API pour les paris
│   ├── crud.py                  # Opérations CRUD
│   └── worker.py                # Workers RQ (optionnel)
├── requirements.txt             # Dépendances Python
└── Dockerfile                   # Image Docker
```

## 🎨 Personnalisation

### Ajouter un nouvel événement

```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "team1": "Bayern Munich",
    "team2": "Dortmund",
    "date": "2024-01-20T19:00:00",
    "odds_team1": 1.8,
    "odds_draw": 3.5,
    "odds_team2": 2.1
  }'
```

### Ajouter des joueurs

```bash
curl -X POST http://localhost:8000/api/players \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "team": "Bayern Munich",
    "name": "Müller",
    "number": 25,
    "position": "FW",
    "photo_url": "https://...",
    "attack": 89,
    "defense": 45,
    "speed": 83,
    "strength": 84,
    "dexterity": 88,
    "stamina": 85
  }'
```

## 🔐 Sécurité

- ✅ CORS configuré pour le développement
- ✅ Validation des données avec FastAPI
- ⚠️ À implémenter: Authentification utilisateur
- ⚠️ À implémenter: Autorisation/permissions
- ⚠️ À implémenter: Validation des montants de pari
- ⚠️ À implémenter: Limite de pari par événement

## 🐛 Troubleshooting

### La base de données ne se connecte pas
```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps

# Vérifier les logs
docker-compose logs db
```

### Les requêtes API échouent (CORS)
- Vérifier que le backend s'exécute sur le port 8000
- Vérifier la configuration CORS dans `main.py`

### Les données de test ne s'affichent pas
- Appeler `/api/seed-data` pour créer les données
- Vérifier que la base de données est vide (première exécution)

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Mantine UI](https://mantine.dev/)
- [SQLModel](https://sqlmodel.tiangolo.com/)

## 👨‍💻 Auteur

Créé pour le projet IA2 dialzeb - Système de Paris Sportifs

## 📄 Licence

Voir LICENSE
