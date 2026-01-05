# 🚀 Guide de Démarrage Rapide

## Installation avec Docker (Recommandé)

### 1. Démarrer tous les services
```bash
cd c:\Users\alifa\Desktop\projetIA2dialzeb
docker-compose up -d
```

### 2. Attendre que tout soit prêt (environ 30 secondes)
```bash
docker-compose logs -f backend
```

### 3. Initialiser les données
```bash
# Option 1: Via l'API
curl -X POST http://localhost:8000/api/seed-data

# Option 2: Via le script Python (si développement local)
cd backend
python init_db.py
```

### 4. Accéder à l'application
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **API Interactive**: http://localhost:8000/redoc

---

## Installation Locale (Développement)

### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev

# Accès: http://localhost:5173
```

### Backend

```bash
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement (optionnel)
# Créer un fichier .env
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sports
# REDIS_URL=redis://localhost:6379

# Démarrer le serveur
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Accès: http://localhost:8000
```

---

## 📱 Utilisation de la Plateforme

### Vue d'ensemble
L'application a 3 onglets principaux:

#### 1️⃣ **Événements**
- Affiche tous les matches de football disponibles
- Voir les cotes pour chaque résultat (1, nul, 2)
- Dates et statuts des événements

#### 2️⃣ **Parier**
- Sélectionner un événement
- Consulter les joueurs avec leurs statistiques
- Affichage type FIFA:
  - Photo du joueur
  - Critères: Attaque, Défense, Vitesse, Force, Dextérité, Endurance
- Placer des paris sur les résultats
- Confirmer le montant et les gains potentiels

#### 3️⃣ **Mes Paris**
- Historique complet de vos paris
- Statistiques: Total misé, Gains potentiels, Taux de réussite
- Statuts: En attente, Gagné, Perdu, Annulé
- Voir les détails de chaque pari

---

## 🔧 Commandes Utiles

### Docker Compose
```bash
# Voir le statut
docker-compose ps

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Supprimer tout (attention!)
docker-compose down -v
```

### Base de Données
```bash
# Accéder à PostgreSQL
docker exec -it projetia2dialzeb-db-1 psql -U postgres -d sports

# Voir les tables
\dt

# Compter les événements
SELECT COUNT(*) FROM event;

# Quitter
\q
```

### Frontend
```bash
# Build de production
npm run build

# Prévisualiser le build
npm run preview
```

### Backend
```bash
# Créer les tables uniquement
python -c "from app.models import *; from sqlmodel import SQLModel, create_engine; engine = create_engine('postgresql://postgres:postgres@localhost:5432/sports'); SQLModel.metadata.create_all(engine)"

# Seed les données de test
python init_db.py
```

---

## 🧪 Tester l'API avec curl

### Lister les événements
```bash
curl http://localhost:8000/api/events
```

### Lister les joueurs d'un événement
```bash
curl http://localhost:8000/api/events/1/players
```

### Placer un pari
```bash
curl -X POST http://localhost:8000/api/bets \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "bet_type": "team1",
    "amount": 10.0,
    "odds": 1.45,
    "user_id": 1
  }'
```

### Voir mes paris
```bash
curl "http://localhost:8000/api/my-bets?user_id=1"
```

### Créer les données de test
```bash
curl -X POST http://localhost:8000/api/seed-data
```

---

## ❌ Troubleshooting

### Port déjà en utilisation
```bash
# Trouver le processus
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Arrêter le processus
kill -9 <PID>
```

### Base de données non accessible
```bash
# Vérifier la connexion
docker-compose logs db

# Redémarrer
docker-compose restart db

# Ou recréer
docker-compose down -v
docker-compose up -d
```

### Module non trouvé
```bash
# Frontend
rm -rf node_modules package-lock.json
npm install

# Backend
pip install --upgrade -r requirements.txt
```

### CORS Errors
- ✅ Le CORS est déjà configuré dans `main.py`
- Vérifier que le backend s'exécute sur le port 8000

---

## 📊 Structure du Projet

```
projetIA2dialzeb/
├── frontend/                    # Application React Vite
│   ├── src/
│   │   ├── App.jsx             # Composant principal (3 onglets)
│   │   ├── components/
│   │   │   ├── EventsList.jsx      # Liste des événements
│   │   │   ├── BettingDashboard.jsx # Interface de paris
│   │   │   └── MyBets.jsx          # Historique
│   │   └── styles.css
│   ├── package.json
│   └── Dockerfile
│
├── backend/                     # API FastAPI + Base de données
│   ├── app/
│   │   ├── main.py             # Application FastAPI
│   │   ├── models.py           # Modèles (Event, Player, Bet)
│   │   ├── betting_routes.py   # Routes des paris
│   │   └── crud.py             # Opérations CRUD
│   ├── requirements.txt
│   ├── Dockerfile
│   └── init_db.py              # Script d'initialisation
│
├── docker-compose.yml          # Configuration Docker
└── FOOTBALL_BETTING_README.md  # Documentation complète
```

---

## 🎯 Prochaines Étapes

1. **Authentification**: Ajouter login/registration
2. **Paiements**: Intégrer Stripe ou similar
3. **Statistiques Avancées**: Graphiques et analyses
4. **Notifications**: Email/SMS pour les résultats
5. **Mobile App**: React Native pour mobile
6. **Live Updates**: WebSocket pour les mises à jour en direct

---

## 📚 Documentation

- [Documentation Complète](./FOOTBALL_BETTING_README.md)
- [FastAPI Docs](http://localhost:8000/docs) - Interactive API docs
- [API Redoc](http://localhost:8000/redoc) - Alternative API docs

---

## 💡 Tips

- Les photos des joueurs sont des placeholders (via.placeholder.com)
- Vous pouvez remplacer les URLs de photos par vos propres images
- Les cotes sont demo, à adapter avec une API de cotes réelle
- Les critères FIFA sont générés aléatoirement, à personnaliser

---

## 🆘 Besoin d'aide?

1. Vérifier les logs: `docker-compose logs`
2. Consulter la documentation complète
3. Vérifier les endpoint sur http://localhost:8000/docs

Bon Paris! ⚽💰
