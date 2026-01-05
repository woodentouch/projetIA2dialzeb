# 🎯 Complete Setup & Testing Guide

## 🚀 Quick Start (3 Commands)

```bash
# 1. Start all services
docker-compose up -d --build

# 2. Wait 30 seconds for services to be ready, then seed data
sleep 30 && curl -X POST http://localhost:8000/api/seed-data

# 3. Open browser
open http://localhost:5173
```

## 📦 What's Been Improved

### ✅ Advanced Bayesian Prediction Model
- **Player statistics integration** - Team quality affects predictions
- **Form analysis** - Recent 5 matches weighted by recency
- **Head-to-head history** - Historical matchups influence predictions
- **Home advantage modeling** - 30% boost for home teams
- **Confidence intervals** - Uncertainty quantification for goals
- **Monte Carlo simulation** - 10,000 samples for accurate probabilities

### ✅ Enhanced Prediction Routes
- **Intelligent caching** - 15-minute cache to reduce computation
- **8 new endpoints**:
  - `/api/predict-match` - Full match prediction
  - `/api/team-stats` - Comprehensive team statistics
  - `/api/head-to-head` - H2H history between teams
  - `/api/train-model` - Manual model retraining
  - `/api/model-info` - Model state information
  - `/api/predict-tournament` - Batch predictions
  - `/api/clear-cache` - Clear prediction cache
  - `/api/export-model` - Export model state

### ✅ Realistic Seed Data
- **35+ historical matches** across 6 months
- **50+ world-class players** with realistic FIFA stats
- **10 major teams**: PSG, Lyon, Manchester United, Liverpool, Real Madrid, Barcelona, Bayern Munich, Borussia Dortmund, Arsenal, Chelsea
- **Realistic score distributions** following actual football statistics

### ✅ New Prediction Dashboard
- **Visual probability displays** with progress bars
- **AI recommendations** with confidence levels
- **Expected goals predictions** with confidence intervals
- **Most likely scores** (top 5)
- **Over/Under predictions** (1.5, 2.5, 3.5 goals)
- **Both teams to score probability**
- **Team form visualization** (W/D/L badges)
- **Head-to-head statistics**
- **Model retraining button**

## 🔧 Manual Setup (If Docker Issues)

### Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sports"
export REDIS_URL="redis://localhost:6379"

# Initialize database (make sure PostgreSQL is running)
python init_db.py

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Seed Data
```bash
curl -X POST http://localhost:8000/api/seed-data
```

## 📊 Testing the Predictions

### 1. Test Basic Prediction
```bash
curl -X POST "http://localhost:8000/api/predict-match?team1=PSG&team2=Lyon" | jq
```

### 2. Get Team Statistics
```bash
curl http://localhost:8000/api/team-stats | jq
```

### 3. Check Head-to-Head
```bash
curl "http://localhost:8000/api/head-to-head?team1=Real%20Madrid&team2=Barcelona" | jq
```

### 4. Get Model Info
```bash
curl http://localhost:8000/api/model-info | jq
```

### 5. Predict Multiple Matches
```bash
curl -X POST http://localhost:8000/api/predict-tournament \
  -H "Content-Type: application/json" \
  -d '[
    {"team1": "PSG", "team2": "Lyon"},
    {"team1": "Real Madrid", "team2": "Barcelona"}
  ]' | jq
```

### 6. Retrain Model
```bash
curl -X POST "http://localhost:8000/api/train-model?force=true" | jq
```

## 🎮 Using the Frontend

### Tab 1: Events
- View all upcoming matches
- See current betting odds
- Match dates and times

### Tab 2: AI Predictions ⭐ NEW!
1. Select a match from dropdown
2. View comprehensive prediction:
   - Win/Draw/Loss probabilities
   - Recommended betting odds
   - Expected goals with confidence intervals
   - Most likely exact scores
   - Over/Under predictions
   - Team form analysis
   - AI recommendation with confidence level
3. Click "Retrain Model" to update with latest data

### Tab 3: Place Bets
1. Select event
2. View odds
3. See player statistics
4. Place bet with amount
5. See potential winnings

### Tab 4: My Bets
- View betting history
- Total staked
- Potential winnings
- Bet status tracking

## 🧪 Advanced Testing Scenarios

### Scenario 1: Complete Prediction Workflow
```bash
# 1. Reset and seed fresh data
curl -X POST http://localhost:8000/api/reset-data
curl -X POST http://localhost:8000/api/seed-data

# 2. Train model
curl -X POST http://localhost:8000/api/train-model

# 3. Get predictions for all matches
curl -X POST http://localhost:8000/api/predict-tournament \
  -H "Content-Type: application/json" \
  -d '[
    {"team1": "PSG", "team2": "Lyon"},
    {"team1": "Manchester United", "team2": "Liverpool"},
    {"team1": "Real Madrid", "team2": "Barcelona"},
    {"team1": "Bayern Munich", "team2": "Borussia Dortmund"},
    {"team1": "Arsenal", "team2": "Chelsea"}
  ]' | jq '.tournament_predictions[] | {match: "\(.team1) vs \(.team2)", recommendation: .recommendation}'
```

### Scenario 2: Analyze Prediction Confidence
```bash
# Get prediction with detailed confidence metrics
curl -X POST "http://localhost:8000/api/predict-match?team1=Real%20Madrid&team2=Barcelona" | jq '{
  match: "\(.team1) vs \(.team2)",
  confidence: .confidence,
  recommendation: .recommendation,
  most_likely: .most_likely_scores[0],
  home_win_prob: .outcome_probabilities.home_win
}'
```

### Scenario 3: Compare Team Statistics
```bash
# Get stats for all teams
curl http://localhost:8000/api/team-stats | jq 'to_entries[] | {
  team: .key,
  attack: .value.strength_ratings.attack_strength,
  defense: .value.strength_ratings.defense_strength,
  form: .value.strength_ratings.form_score
}'
```

## 📈 Understanding the Predictions

### Confidence Levels
- **High (>70%)**: Strong recommendation, model has good data
- **Medium (50-70%)**: Moderate confidence, use with caution
- **Low (<50%)**: Insufficient data, avoid betting

### Probability Interpretation
- **>60% probability**: Strong favorite
- **40-60%**: Competitive match
- **<40%**: Underdog

### Expected Goals
- Uses Poisson distribution
- Factors in attack strength, defense strength, form, player quality
- Confidence intervals show uncertainty range

### Most Likely Scores
- Calculated from 10,000 Monte Carlo simulations
- Top 5 most probable exact scorelines
- Percentages show likelihood

## 🐛 Troubleshooting

### Issue: "Model not fitted yet"
**Solution**: 
```bash
curl -X POST http://localhost:8000/api/train-model
```

### Issue: No predictions available
**Solution**: Make sure data is seeded
```bash
curl -X POST http://localhost:8000/api/seed-data
```

### Issue: Frontend can't connect to backend
**Solution**: Check if backend is running on port 8000
```bash
curl http://localhost:8000/health
```

### Issue: Predictions seem cached
**Solution**: Clear cache
```bash
curl -X DELETE http://localhost:8000/api/clear-cache
```

### Issue: Want fresh predictions
**Solution**: Force retrain
```bash
curl -X POST "http://localhost:8000/api/train-model?force=true"
```

## 🎯 Key Improvements Summary

### Backend
- ✅ Advanced Bayesian model with player stats (300+ lines)
- ✅ 8 new prediction endpoints
- ✅ Intelligent caching system
- ✅ 35+ historical matches for training
- ✅ 50+ realistic player profiles
- ✅ Form analysis (last 5 matches)
- ✅ Head-to-head integration
- ✅ Confidence scoring
- ✅ Monte Carlo simulations
- ✅ Export/import model state

### Frontend
- ✅ New PredictionDashboard component (400+ lines)
- ✅ Visual probability displays
- ✅ Interactive charts and progress bars
- ✅ AI recommendations
- ✅ Real-time model retraining
- ✅ Comprehensive match analysis
- ✅ Team form visualization
- ✅ Confidence indicators

### API Enhancements
- ✅ RESTful design
- ✅ Query parameter validation
- ✅ Error handling
- ✅ CORS configuration
- ✅ Response caching
- ✅ Batch predictions
- ✅ Model introspection

## 🚀 Next Steps (Optional Enhancements)

1. **Add more teams and leagues**
2. **Integrate real API data** (football-data.org, API-Football)
3. **Historical accuracy tracking** (compare predictions to actual results)
4. **User authentication and profiles**
5. **Payment integration** (Stripe/PayPal)
6. **Live score updates** (WebSocket)
7. **Advanced analytics dashboard** (ROI, win rates)
8. **Mobile app** (React Native)
9. **Social features** (share predictions, leaderboards)
10. **ML model improvements** (neural networks, ensemble methods)

## 📞 Support

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Restart services: `docker-compose restart`
3. Clear everything: `docker-compose down -v && docker-compose up -d --build`

## 🎉 You're All Set!

Your advanced football betting prediction platform is now ready with:
- ✅ Sophisticated Bayesian AI predictions
- ✅ Beautiful interactive frontend
- ✅ Comprehensive API
- ✅ Realistic test data
- ✅ Production-ready architecture

**Enjoy predicting match outcomes with AI! ⚽🎯**
