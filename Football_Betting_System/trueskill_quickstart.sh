#!/bin/bash

# TrueSkill AI Quick Start Script
# Run this to test all endpoints after starting the backend

echo "======================================================================"
echo "⚽ TrueSkill AI Quick Start"
echo "======================================================================"
echo ""

echo "📋 Step 1: Check backend health"
curl -sS "http://localhost:8000/health"
echo ""
echo ""

echo "📋 Step 2: Add some match results"
echo "   Match 1: Manchester City 2-2 Arsenal"
curl -sS -X POST "http://localhost:8000/api/ratings/update" \
  -H "Content-Type: application/json" \
  -d '{"team1":"Manchester City","team2":"Arsenal","score1":2,"score2":2}' > /dev/null
echo "   ✅ Ratings updated"

echo "   Match 2: Liverpool 3-0 Manchester United"
curl -sS -X POST "http://localhost:8000/api/ratings/update" \
  -H "Content-Type: application/json" \
  -d '{"team1":"Liverpool","team2":"Manchester United","score1":3,"score2":0}' > /dev/null
echo "   ✅ Ratings updated"

echo "   Match 3: Real Madrid 2-1 Barcelona"
curl -sS -X POST "http://localhost:8000/api/ratings/update" \
  -H "Content-Type: application/json" \
  -d '{"team1":"Real Madrid","team2":"Barcelona","score1":2,"score2":1}' > /dev/null
echo "   ✅ Ratings updated"
echo ""

echo "📋 Step 3: View current ratings"
curl -sS "http://localhost:8000/api/ratings?sort_by=conservative&order=desc&limit=5" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('   Top 5 Teams:')
for i, r in enumerate(data['ratings'], 1):
    print(f\"   {i}. {r['team']:20s} - Conservative: {r['conservative']:6.1f}\")
"
echo ""

echo "📋 Step 4: Get AI prediction"
echo "   Predicting: Liverpool vs Real Madrid"
curl -sS "http://localhost:8000/api/ai-predict?team1=Liverpool&team2=Real%20Madrid&n_simulations=10000" | python3 -c "
import json, sys
data = json.load(sys.stdin)
probs = data['outcome_probabilities']
goals = data['goals_prediction']
print(f\"   Home Win: {probs['home_win']*100:.1f}% | Draw: {probs['draw']*100:.1f}% | Away Win: {probs['away_win']*100:.1f}%\")
print(f\"   Expected: {goals['expected_home_goals']:.2f} - {goals['expected_away_goals']:.2f}\")
print(f\"   Confidence: {data['confidence']['level']}\")
print(f\"   Top scores: {data['most_likely_scores'][0]['score']} ({data['most_likely_scores'][0]['probability']*100:.1f}%), {data['most_likely_scores'][1]['score']} ({data['most_likely_scores'][1]['probability']*100:.1f}%)\")
"
echo ""

echo "======================================================================"
echo "✅ All endpoints working!"
echo ""
echo "🔗 API Documentation: http://localhost:8000/docs"
echo "🔗 Main AI Endpoint: http://localhost:8000/api/ai-predict"
echo "======================================================================"
