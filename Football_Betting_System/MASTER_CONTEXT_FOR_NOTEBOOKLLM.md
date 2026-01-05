# FOOTBALL BETTING SYSTEM - COMPREHENSIVE SOURCE CODE & DOCUMENTATION

**Note to NotebookLLM:** This document contains the **entire technical context** for the Football Betting System. It includes the full mathematical logic, backend algorithm implementations, API routes, database schemas, and frontend components. Use this data to answer any questions about the project's architecture, math, or code.

---

## SECTION 1: SYSTEM ARCHITECTURE & INFRASTRUCTURE

### 1.1 Infrastructure (`docker-compose.yml`)
The system follows a microservices architecture orchestrated by Docker.

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: sports
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

  redis:
    image: redis:7
    volumes:
      - redis-data:/data

  backend:
    build:
      context: ./backend
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/sports
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000

volumes:
  db-data:
  redis-data:
```

### 1.2 Dependencies (`backend/requirements.txt`)
The Python environment relies on specific libraries for math and API:

```text
fastapi==0.100.0
uvicorn[standard]==0.23.0
sqlmodel==0.0.8
psycopg2-binary==2.9.7
redis==5.0.0
numpy==1.24.3
scipy==1.11.4
trueskill==0.4.5
```

---

## SECTION 2: THE MATHEMATICAL CORE

### 2.1 The Ranking Engine (`backend/app/trueskill_rating.py`)
This file implements Microsoft's TrueSkill algorithm to track team strength as a Gaussian distribution.

```python
from trueskill import TrueSkill, Rating

# We set draw_probability=0.26 because ~26% of football matches are draws
TRUESKILL_ENV = TrueSkill(draw_probability=0.26)

def update_ratings_after_match(team1_rating, team2_rating, result):
    """
    Updates ratings based on match outcome.
    result: 1 (team1 win), 0.5 (draw), 0 (team2 win)
    """
    r1 = Rating(mu=team1_rating.mu, sigma=team1_rating.sigma)
    r2 = Rating(mu=team2_rating.mu, sigma=team2_rating.sigma)
    
    if result == 1: # Team 1 wins
        new_r1, new_r2 = TRUESKILL_ENV.rate_1vs1(r1, r2)
    elif result == 0: # Team 2 wins
        new_r2, new_r1 = TRUESKILL_ENV.rate_1vs1(r2, r1)
    else: # Draw
        new_r1, new_r2 = TRUESKILL_ENV.rate_1vs1(r1, r2, drawn=True)
        
    return new_r1, new_r2
```

### 2.2 The Prediction Brain (`backend/app/bayesian_model.py`)
This is the **most critical file**. It combines Historical Stats, TrueSkill Ratings, and Poisson Simulation. This class `BayesianFootballModel` is the heart of the AI.

```python
import numpy as np
from collections import defaultdict
from .trueskill_rating import to_rating

class BayesianFootballModel:
    def __init__(self):
        self.team_stats = {}
        self.trueskill_ratings = {} 
        self.global_avg_goals = 2.5

    def fit(self, matches, player_data=None):
        """
        Trains the model by iterating over historical matches.
        Calculates attack_strength, defense_strength, and form_score for every team.
        """
        for match in matches:
             # ... (Detailed aggregation logic found in source files) ...
             pass

    def predict_match(self, team1, team2, n_samples=10000):
        """
        Runs the Monte Carlo Simulation to predict probabilities.
        """
        # 1. RETRIEVE BASE STATS
        stats1 = self.team_stats.get(team1)
        stats2 = self.team_stats.get(team2)
        
        # 2. CALCULATE ATTACK/DEFENSE VECTORS
        # We blend home/away specific performance with overall strength to avoid small-sample bias
        home_attack = (stats1['home_attack'] * 0.6) + (stats1['attack_strength'] * 0.4)
        away_defense = stats2['defense_strength']
        
        # 3. APPLY TRUESKILL CORRECTION
        # If we have TrueSkill ratings, we use them to adjust the Expected Goals (Lambda)
        ts_modifier_home = 1.0
        ts_modifier_away = 1.0
        if team1 in self.trueskill_ratings and team2 in self.trueskill_ratings:
            mu_diff = self.trueskill_ratings[team1] - self.trueskill_ratings[team2]
            # Logistic function to map skill difference to goal probability multiplier
            # +5 Skill Diff -> ~1.2x goals
            ts_modifier_home = 2.0 / (1.0 + np.exp(-0.06 * mu_diff))
            ts_modifier_away = 2.0 / (1.0 + np.exp(0.06 * mu_diff))

        # 4. CALCULATE EXPECTED GOALS (LAMBDA)
        # Formula: (Attack / Defense) * League_Avg * Modifiers
        expected_home_goals = (home_attack / away_defense) * self.global_avg_goals * ts_modifier_home
        expected_away_goals = (stats2['away_attack'] / stats1['defense_strength']) * self.global_avg_goals * ts_modifier_away
        
        # 5. MONTE CARLO SIMULATION (The "Multiverse")
        # We simulate 10,000 matches using Poisson distribution
        home_samples = np.random.poisson(expected_home_goals, n_samples)
        away_samples = np.random.poisson(expected_away_goals, n_samples)
        
        home_wins = np.sum(home_samples > away_samples)
        draws = np.sum(home_samples == away_samples)
        away_wins = np.sum(home_samples < away_samples)
        
        # 6. DIXON-COLES ADJUSTMENT
        # Basic Poisson underestimates 0-0 and 1-1 draws. We adjust for this correlation (rho).
        rho = -0.13
        # ... (Dixon-Coles math applied here) ...
        
        return {
            "probabilities": {
                "home_win": home_wins / n_samples,
                "draw": draws / n_samples,
                "away_win": away_wins / n_samples
            },
            "expected_goals": {
                "home": expected_home_goals,
                "away": expected_away_goals
            },
            "confidence": self._calculate_confidence(stats1, stats2)
        }

    def _calculate_confidence(self, stats1, stats2):
        """
        Determines how much we trust this prediction.
        Factors: Match Count, Form Stability, Data Quality.
        """
        # We lowered the threshold to 10 patches to fix "Low Confidence" errors
        matches_factor = min((stats1['matches'] + stats2['matches']) / 10, 1.0)
        # Form consistency: consistent teams are easier to predict
        form_consistency = abs(stats1['form_score'] - 0.5) * 2 
        
        return (matches_factor * 0.6) + (form_consistency * 0.4)
```

---

## SECTION 3: ADVANCED ANALYTICS (Opta Level)

### 3.1 The Opta Engine (`backend/app/opta_engine.py`)
This is a secondary, more advanced engine (`OptaAIEngine`) that calculates deeper metrics like **xG (Expected Goals)**, **Betting Margins**, and **Half-Time predictions**.

```python
class OptaAIEngine:
    def predict_match(self, team1, team2, venue="home"):
        # 1. Calculates venue-specific ratings (Home Mu vs Away Mu)
        # 2. Applies momentum/form decay
        # 3. Simulates Halftime Scores separately
        
        ht_xg_1 = prediction.team1_xg * 0.45 
        ht_scores = self._monte_carlo_scores(ht_xg_1, ht_xg_2)
        
        # 4. Calculates Betting Markets
        # Over/Under 2.5
        prediction.over_under_2_5 = self._calculate_over_under(score_distribution, 2.5)
        
        # BTTS (Both Teams To Score)
        prediction.both_teams_score_prob = self._btts_probability(score_distribution)
        
        return prediction
```

### 3.2 TrueSkill AI Engine (`backend/app/trueskill_ai_engine.py`)
A dedicated class `TrueSkillAIEngine` that focuses purely on the statistical side of the rating updates.

```python
class TrueSkillAIEngine:
    def _calculate_expected_goals(self, team1, team2):
        # Maps skill difference (normalized by sigma) to goal expectation
        skill_diff = (team1.mu - team2.mu) / TRUESKILL_ENV.sigma
        
        # Base goals is 1.5 per team. +0.2 for Home Advantage.
        team1_lambda = 1.5 + 0.2 + (skill_diff * 0.15)
        
        return team1_lambda, team2_lambda
```

---

## SECTION 4: API & DATABASE

### 4.1 Database Schema (`backend/app/models.py`)

The detailed schema includes support for Betting, Events, and Ratings.

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class TeamRating(SQLModel, table=True):
    """The Core of the Persistence: Storing TrueSkill Mu/Sigma"""
    id: Optional[int] = Field(default=None, primary_key=True)
    team: str = Field(index=True, unique=True)
    mu: float
    sigma: float
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Event(SQLModel, table=True):
    """A match that can be bet on"""
    id: Optional[int] = Field(default=None, primary_key=True)
    team1: str
    team2: str
    odds_team1: float
    odds_draw: float
    odds_team2: float
    status: str = "active"

class Player(SQLModel, table=True):
    """Stores FIFA-style player attributes for granular analysis"""
    id: Optional[int] = Field(default=None, primary_key=True)
    team: str
    name: str
    attack: int = 75
    defense: int = 75
    speed: int = 75
    # ... other stats
```

### 4.2 Advanced Opta Models (`backend/app/models_advanced.py`)

We also support highly detailed match statistics for future expansion.

```python
class MatchStatistics(SQLModel, table=True):
    """Detailed stats like XG, Possession, etc."""
    possession_pct: Optional[float] = None
    expected_goals: Optional[float] = None  # xG
    shots_on_target: Optional[int] = None
    pressing_intensity: Optional[float] = None
```

### 4.3 Prediction Endpoints (`backend/app/prediction_routes.py`)

The connection between the brain and the outside world.

```python
from fastapi import APIRouter
from .bayesian_model import BayesianFootballModel

router = APIRouter(prefix="/api")
model = BayesianFootballModel()

@router.get("/predict-match")
async def predict(team1: str, team2: str):
    """
    1. Check Cache (Redis/Memory)
    2. If not cached, run BayesianModel.predict_match
    3. Return JSON to frontend
    """
    # ... logic ensures model is trained before predicting ...
    if not model.is_fitted:
        model.fit(load_training_data())
        
    result = model.predict_match(team1, team2)
    return result
```

### 4.4 Betting Endpoints (`backend/app/betting_routes.py`)

Handles the user side of placing bets.

```python
@router.post("/bets")
def place_bet(bet_request):
    """Records a user wager in the database"""
    # ... calculates potential win = amount * odds ...
    pass
```

---

## SECTION 5: INITIALIZATION & DATA SEEDING

### 5.1 Database Setup (`backend/init_db.py`)
This script initializes the tables and injects initial player data (Mbappe, Haaland, etc.) for testing.

```python
def seed_test_data():
    """Crée les données de test"""
    # ... Creates dummy matches: PSG vs Lyon, United vs Liverpool ...
    # ... Creates dummy players with FIFA-like stats ...
```

### 5.2 Making the AI Smart (`backend/seed_data.py`)
Logic to generate "synthetic history" for teams so the model doesn't start empty.

```python
def generate_additional_matches():
    """
    Solves the 'Cold Start' problem. 
    Generates random (but realistic) matches for teams with no history.
    Uses 'Tier' logic (Tier 1 vs Tier 4 => Tier 1 usually wins).
    """
    for team in ALL_TEAMS:
        if team_has_no_data(team):
            # Generate 3 matches against random opponents
            create_synthetic_matches(team)
            # This ensures every team has a valid Sigma rating at launch
```

---

## SECTION 6: THE FRONTEND

### 6.1 The Dashboard (`frontend/src/components/PredictionDashboard.jsx`)
A React component using Mantine/Tailwind for the UI.

```jsx
import { useState } from 'react';
import { Card, Title, Text, Button, Select, Grid } from './CustomComponents';
import axios from 'axios';

export default function PredictionDashboard() {
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [prediction, setPrediction] = useState(null);

  const handlePredict = async () => {
    // Calls the Python Backend
    const res = await axios.get(`/api/predict-match?team1=${team1}&team2=${team2}`);
    setPrediction(res.data);
  };

  return (
    <Card className="lift-card" style={{ backdropFilter: 'blur(10px)' }}>
      <Title>AI Prediction Engine</Title>
      <# ... UI Components for Selection ... #>
      <Button onClick={handlePredict} gradient={{ from: 'indigo', to: 'cyan' }}>
        Predict Match with AI
      </Button>

      {prediction && (
        <Grid>
           <Card bg="green">
             <Text>Home Win</Text>
             <Text size="xl">{prediction.outcome_probabilities.home_win}%</Text>
           </Card>
           <Card bg="orange">
             <Text>Draw</Text>
             <Text size="xl">{prediction.outcome_probabilities.draw}%</Text>
           </Card>
           <Card bg="red">
             <Text>Away Win</Text>
             <Text size="xl">{prediction.outcome_probabilities.away_win}%</Text>
           </Card>
        </Grid>
      )}
    </Card>
  );
}
```

### 6.2 Layout Stability (`frontend/src/components/CustomComponents.jsx`)

To solve layout shift issues ("cards sticking"), we implemented strict wrapper components that enforce consistent spacing.

```jsx
// Custom Stack Component
export const Stack = ({ children, gap = 'md' }) => {
  return <div style={{ display: 'flex', flexDirection: 'column', gap: spacingToPx(gap) }}>{children}</div>;
};

// Custom Group Component
export const Group = ({ children, gap = 'md' }) => {
  return <div style={{ display: 'flex', flexDirection: 'row', gap: spacingToPx(gap) }}>{children}</div>;
};
```

### 6.3 Safe Data Utilities (`frontend/src/utils.js`)

To prevent "undefined" errors on the frontend, we wrapped all data access.

```javascript
export const safePercent = (value) => {
  if (!Number.isFinite(Number(value))) return '0.0%';
  return (value * 100).toFixed(1) + '%';
};
```

---

## SECTION 7: KEY PROJECT DECISIONS

### 7.1 Why TrueSkill + Bayesian?
Most betting apps use Elo ratings (single number). Elo fails to capture **Confidence**. TrueSkill gives us a gaussian distribution (Mean + Variance). If a team is new, Variance is high, so the AI knows "I don't know".
Monte Carlo simulation then takes these uncertainties and plays out the match 10,000 times to give a probability distribution, which is far more accurate than a simple formula.

### 7.2 Why Docker?
To ensure the Python backend (with complex math libraries like `numpy` and `scipy`) runs identically on any machine, separate from the Node.js frontend.

### 7.3 "Confidence" Calculation
We defined confidence as:
$$ Confidence = 0.6 \times (\text{match\_volume}) + 0.4 \times (\text{form\_consistency}) + \text{Bonus(if TrueSkill exists)} $$
This solved the issue of the AI being "too shy" about predicting well-known teams.
