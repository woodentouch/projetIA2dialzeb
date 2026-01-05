# ⚽ TrueSkill AI Prediction Engine

## 🤖 Overview

The project now features a **fully operational TrueSkill AI engine** as its core prediction model. TrueSkill is a Bayesian skill rating system developed by Microsoft Research that uses Gaussian distributions to model team/player skill levels with uncertainty.

## 🚀 What is TrueSkill?

TrueSkill models each team's skill as a normal distribution:
- **μ (mu)**: Mean skill level (default: 25)
- **σ (sigma)**: Skill uncertainty (default: 8.33)
- **Conservative Rating**: μ - 3σ (the "true skill" estimate)

After each match, both teams' ratings are updated based on:
- Match outcome (win/draw/loss)
- Score difference
- Pre-match expectations (upset victories = bigger rating changes)

## 📡 API Endpoints

### 1. **Main AI Prediction** ⭐
```bash
GET /api/ai-predict?team1={home}&team2={away}&n_simulations={count}
```

**Returns comprehensive match prediction:**
- Win/Draw/Loss probabilities
- Expected goals for both teams
- Top 10 most likely scorelines
- Over/Under 2.5 goals
- Both Teams To Score (BTTS)
- Fair betting odds (with 5% margin)
- Confidence level (HIGH/MEDIUM/LOW)
- AI recommendation

**Example:**
```bash
curl "http://localhost:8000/api/ai-predict?team1=Liverpool&team2=Bayern%20Munich&n_simulations=20000"
```

**Sample Response:**
```json
{
  "model": "TrueSkill AI Engine v1.0",
  "teams": {
    "home": {
      "name": "Liverpool",
      "rating": {"mu": 34.9, "sigma": 5.4, "conservative": 18.7}
    },
    "away": {
      "name": "Bayern Munich",
      "rating": {"mu": 31.6, "sigma": 6.5, "conservative": 12.2}
    }
  },
  "outcome_probabilities": {
    "home_win": 0.552,
    "draw": 0.143,
    "away_win": 0.305
  },
  "goals_prediction": {
    "expected_home_goals": 1.76,
    "expected_away_goals": 1.44,
    "expected_total_goals": 3.20
  },
  "betting_odds": {
    "home_odds": 1.90,
    "draw_odds": 7.33,
    "away_odds": 3.45
  },
  "most_likely_scores": [
    {"score": "1-1", "probability": 0.103},
    {"score": "2-1", "probability": 0.091},
    {"score": "1-2", "probability": 0.074}
  ],
  "over_under": {
    "over_2.5": 0.619,
    "under_2.5": 0.381
  },
  "both_teams_score": 0.631,
  "confidence": {
    "level": "LOW",
    "prediction_confidence": 0.314,
    "rating_uncertainty": 0.712
  },
  "recommendation": "AI predicts home win with 55.2% confidence. Fair odds: 1.9 ⚠️ Low confidence - ratings still stabilizing.",
  "simulations": 20000
}
```

### 2. **Update Ratings After Match**
```bash
POST /api/ratings/update
Content-Type: application/json

{
  "team1": "PSG",
  "team2": "Lyon",
  "score1": 3,
  "score2": 1,
  "store_as_match": true
}
```

**Returns:** Updated ratings + next match probabilities

### 3. **List All Ratings**
```bash
GET /api/ratings?limit=200&sort_by=conservative&order=desc
```

**Sort options:**
- `team`: Alphabetical
- `mu`: Mean skill
- `sigma`: Uncertainty
- `conservative`: Conservative rating (μ - 3σ)

### 4. **Get Single Team Rating**
```bash
GET /api/ratings/{team_name}
```

Auto-creates rating if team doesn't exist (default: μ=25, σ=8.33)

### 5. **Simple Probability Prediction**
```bash
GET /api/predict-rating?team1={home}&team2={away}
```

Lightweight endpoint - returns only win/draw/loss probabilities without Monte Carlo simulation.

## 🧠 How the AI Works

### 1. **Rating Calculation**
- Uses TrueSkill's Bayesian update algorithm
- Factors in skill difference and match outcome
- Reduces uncertainty (σ) over time as teams play more matches

### 2. **Expected Goals Mapping**
```python
skill_diff = team1.mu - team2.mu
expected_home_goals = 1.5 + (skill_diff / 15)  # Range: 0.5 - 3.5
expected_away_goals = 1.5 - (skill_diff / 15)  
```
- Home advantage: +0.2 goals
- Skill difference scales linearly with expected goals

### 3. **Monte Carlo Score Simulation**
- Uses **Poisson distribution** with λ = expected_goals
- Runs N simulations (1,000 - 50,000)
- Generates all score combinations (0-7 goals per team)
- Calculates probabilities from simulation frequencies

### 4. **Confidence Calculation**
```python
confidence = (rating_certainty * 0.4) + (outcome_clarity * 0.6)

rating_certainty = 1 - (avg_sigma / 8.33)  # Lower σ = higher certainty
outcome_clarity = max(p_win, p_draw, p_loss) - 0.33  # Normalized clarity

# Levels:
# HIGH: confidence ≥ 0.65
# MEDIUM: 0.45 ≤ confidence < 0.65
# LOW: confidence < 0.45
```

### 5. **Fair Odds Calculation**
```python
# Convert probability to European odds
fair_odds = 1 / probability

# Add 5% bookmaker margin
offered_odds = fair_odds * 0.95
```

## 📊 Current Ratings (Sample)

| Team | μ | σ | Conservative | Status |
|------|---|---|--------------|--------|
| Liverpool | 34.9 | 5.4 | 18.7 | 🔥 Hot |
| Bayern Munich | 31.6 | 6.5 | 12.2 | ⚡ Strong |
| PSG | 31.6 | 6.5 | 12.2 | ⚡ Strong |
| Real Madrid | 31.6 | 6.5 | 12.2 | ⚡ Strong |
| Arsenal | 24.1 | 5.1 | 8.7 | ✅ Stable |
| Manchester City | 22.5 | 4.6 | 8.7 | ✅ Stable |

## 🎯 Integration with Frontend

The AI is ready to be integrated into your React frontend. Example usage:

```typescript
// services/trueskill.service.ts
export const TrueSkillService = {
  async predictMatch(team1: string, team2: string, simulations = 10000) {
    const response = await fetch(
      `${API_BASE}/api/ai-predict?team1=${team1}&team2=${team2}&n_simulations=${simulations}`
    );
    return await response.json();
  },

  async updateRatings(team1: string, team2: string, score1: number, score2: number) {
    const response = await fetch(`${API_BASE}/api/ratings/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ team1, team2, score1, score2 }),
    });
    return await response.json();
  },

  async getRatings(sortBy = 'conservative', order = 'desc', limit = 100) {
    const response = await fetch(
      `${API_BASE}/api/ratings?sort_by=${sortBy}&order=${order}&limit=${limit}`
    );
    return await response.json();
  },
};
```

## 🔬 Technical Stack

- **TrueSkill Library**: `trueskill==0.4.5` (Bayesian skill rating)
- **SciPy**: `scipy==1.11.4` (Normal distribution CDF calculations)
- **NumPy**: `numpy==1.24.3` (Poisson distribution for score simulation)
- **FastAPI**: High-performance async endpoints
- **PostgreSQL**: Persistent storage for TeamRating table

## 🚧 Future Enhancements

1. **Historical Data Loading**: Import past match results to pre-train ratings
2. **Team Form**: Weight recent matches higher (exponential decay)
3. **Venue Impact**: Model home/away advantage per stadium
4. **Injuries/Suspensions**: Adjust team strength dynamically
5. **League Strength**: Cross-league rating normalization
6. **Multivariate Features**: Weather, referee, head-to-head history
7. **Deep Learning Hybrid**: Combine TrueSkill with neural network for feature engineering

## 📝 Notes

- **Cold Start**: New teams start at μ=25, σ=8.33 (high uncertainty)
- **Convergence**: Ratings stabilize after ~10-15 matches
- **Upset Detection**: Large skill differences can still result in surprises (probabilistic model)
- **Draw Modeling**: Uses draw_probability parameter (configurable, default ~10%)

## 🎉 Status

✅ **FULLY OPERATIONAL** - The TrueSkill AI engine is production-ready and serves as the core prediction model for the platform.

---

**Last Updated**: January 5, 2026  
**Model Version**: v1.0  
**Endpoint**: `http://localhost:8000/api/ai-predict`
