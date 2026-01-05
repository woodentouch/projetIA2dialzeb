# 🔗 Endpoints API - Football Betting Platform

## Base URL
```
http://localhost:8000
```

## Documentation Interactive
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 Endpoints Disponibles

### 🏥 Health Check
```http
GET /health
```
**Réponse** (200 OK):
```json
{"status": "ok"}
```

---

## 🎯 Événements (Events)

### Lister tous les événements
```http
GET /api/events
```

**Exemple curl**:
```bash
curl http://localhost:8000/api/events
```

**Réponse** (200 OK):
```json
{
  "events": [
    {
      "id": 1,
      "team1": "PSG",
      "team2": "Lyon",
      "date": "2024-01-06T19:00:00",
      "status": "active",
      "odds_team1": 1.45,
      "odds_draw": 3.8,
      "odds_team2": 2.7,
      "result": null
    }
  ]
}
```

---

### Obtenir un événement spécifique
```http
GET /api/events/{event_id}
```

**Exemple curl**:
```bash
curl http://localhost:8000/api/events/1
```

**Paramètres**:
- `event_id` (int, required): ID de l'événement

**Réponse** (200 OK):
```json
{
  "id": 1,
  "team1": "PSG",
  "team2": "Lyon",
  "date": "2024-01-06T19:00:00",
  "status": "active",
  "odds_team1": 1.45,
  "odds_draw": 3.8,
  "odds_team2": 2.7,
  "result": null
}
```

---

## 👥 Joueurs (Players)

### Lister les joueurs d'un événement
```http
GET /api/events/{event_id}/players
```

**Exemple curl**:
```bash
curl http://localhost:8000/api/events/1/players
```

**Paramètres**:
- `event_id` (int, required): ID de l'événement

**Réponse** (200 OK):
```json
{
  "players": [
    {
      "id": 1,
      "name": "Mbappé",
      "number": 7,
      "position": "FW",
      "team": "PSG",
      "photo_url": "https://via.placeholder.com/150?text=Mbappe",
      "attack": 94,
      "defense": 38,
      "speed": 96,
      "strength": 76,
      "dexterity": 87,
      "stamina": 89
    }
  ]
}
```

---

## 💰 Paris (Bets)

### Placer un nouveau pari
```http
POST /api/bets
```

**Exemple curl**:
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

**Paramètres** (Body JSON):
- `event_id` (int, required): ID de l'événement
- `bet_type` (str, required): Type de pari (team1, draw, team2, etc.)
- `amount` (float, required): Montant du pari en euros
- `odds` (float, required): Cote au moment du pari
- `user_id` (int, optional): ID de l'utilisateur (défaut: null)

**Réponse** (200 OK):
```json
{
  "id": 1,
  "event_id": 1,
  "bet_type": "team1",
  "amount": 10.0,
  "odds": 1.45,
  "status": "pending",
  "created_at": "2024-01-06T12:00:00",
  "gain_potential": 14.5
}
```

**Erreurs**:
- `404`: Événement non trouvé
- `400`: Événement inactif

---

### Obtenir mes paris
```http
GET /api/my-bets
```

**Exemple curl**:
```bash
curl "http://localhost:8000/api/my-bets?user_id=1"
```

**Paramètres** (Query):
- `user_id` (int, optional): ID de l'utilisateur (défaut: 1)

**Réponse** (200 OK):
```json
{
  "bets": [
    {
      "id": 1,
      "event_id": 1,
      "event_name": "PSG vs Lyon",
      "bet_type": "team1",
      "amount": 10.0,
      "odds": 1.45,
      "status": "pending",
      "created_at": "2024-01-06T12:00:00",
      "gain_potential": 14.5
    }
  ]
}
```

---

### Obtenir un pari spécifique
```http
GET /api/bets/{bet_id}
```

**Exemple curl**:
```bash
curl http://localhost:8000/api/bets/1
```

**Paramètres**:
- `bet_id` (int, required): ID du pari

**Réponse** (200 OK):
```json
{
  "id": 1,
  "event_id": 1,
  "event_name": "PSG vs Lyon",
  "bet_type": "team1",
  "amount": 10.0,
  "odds": 1.45,
  "status": "pending",
  "created_at": "2024-01-06T12:00:00",
  "gain_potential": 14.5
}
```

---

## 🌱 Données de Test

### Créer les données de test
```http
POST /api/seed-data
```

**Exemple curl**:
```bash
curl -X POST http://localhost:8000/api/seed-data
```

**Réponse** (200 OK):
```json
{
  "message": "Données de test créées avec succès",
  "events_created": 3
}
```

**Crée automatiquement**:
- 3 événements: PSG vs Lyon, Man Utd vs Liverpool, Real vs Barcelona
- 18 joueurs avec photos et stats FIFA

---

## 🔄 Flux d'Utilisation Complet

### 1. Récupérer tous les événements
```bash
curl http://localhost:8000/api/events
```

### 2. Récupérer les joueurs d'un événement
```bash
curl http://localhost:8000/api/events/1/players
```

### 3. Placer un pari
```bash
curl -X POST http://localhost:8000/api/bets \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "bet_type": "team1",
    "amount": 20.0,
    "odds": 1.45,
    "user_id": 1
  }'
```

### 4. Voir mes paris
```bash
curl "http://localhost:8000/api/my-bets?user_id=1"
```

### 5. Voir un pari spécifique
```bash
curl http://localhost:8000/api/bets/1
```

---

## 📊 Structure des Données

### Event
```json
{
  "id": 1,
  "team1": "PSG",
  "team2": "Lyon",
  "date": "2024-01-06T19:00:00",
  "status": "active",
  "odds_team1": 1.45,
  "odds_draw": 3.8,
  "odds_team2": 2.7,
  "result": null
}
```

### Player
```json
{
  "id": 1,
  "name": "Mbappé",
  "number": 7,
  "position": "FW",
  "team": "PSG",
  "photo_url": "https://example.com/photo.jpg",
  "attack": 94,
  "defense": 38,
  "speed": 96,
  "strength": 76,
  "dexterity": 87,
  "stamina": 89
}
```

### Bet
```json
{
  "id": 1,
  "event_id": 1,
  "event_name": "PSG vs Lyon",
  "bet_type": "team1",
  "amount": 10.0,
  "odds": 1.45,
  "status": "pending",
  "created_at": "2024-01-06T12:00:00",
  "gain_potential": 14.5
}
```

---

## 🎯 Codes de Statut HTTP

| Code | Signification | Exemple |
|------|---------------|---------|
| 200 | OK - Succès | Événement trouvé |
| 201 | Created - Créé | Pari placé |
| 400 | Bad Request - Mauvaise requête | Événement inactif |
| 404 | Not Found - Non trouvé | Événement inexistant |
| 500 | Server Error - Erreur serveur | Erreur base de données |

---

## 💡 Conseils d'Utilisation

### Pour Tester Rapidement
1. Lancer: `docker-compose up -d`
2. Créer les données: `curl -X POST http://localhost:8000/api/seed-data`
3. Accéder à l'interface: http://localhost:5173

### Avec Postman
1. Importer l'URL: `http://localhost:8000/docs`
2. Tester directement les endpoints
3. Voir les réponses en JSON

### Pour le Développement
1. Consulter http://localhost:8000/docs (Swagger)
2. Les endpoints sont auto-documentés
3. Essayer directement depuis l'interface

---

## 🔐 Sécurité

⚠️ **En Développement**: CORS est ouvert à tous
```python
allow_origins=["*"]
```

✅ **Pour la Production**: À configurer
```python
allow_origins=["https://yourdomain.com"]
```

---

## 📝 Notes

- Les cotes sont des examples (à adapter)
- Les photos des joueurs sont des placeholders
- Les stats des joueurs sont générées aléatoirement
- Les montants de pari n'ont pas de limite (à implémenter)
- Pas de validation de montant minimum (à implémenter)

---

## 🚀 Prochains Endpoints à Ajouter

- [ ] `POST /api/players` - Créer un joueur
- [ ] `PUT /api/events/{id}` - Mettre à jour cotes
- [ ] `POST /api/users/register` - Inscription
- [ ] `POST /api/users/login` - Connexion
- [ ] `DELETE /api/bets/{id}` - Annuler un pari (optionnel)
- [ ] `POST /api/events/{id}/close` - Clôturer un événement

---

Pour plus d'aide, consulter:
- 📖 [QUICK_START.md](./QUICK_START.md)
- 📚 [FOOTBALL_BETTING_README.md](./FOOTBALL_BETTING_README.md)
- 🎮 [USER_GUIDE.md](./USER_GUIDE.md)
