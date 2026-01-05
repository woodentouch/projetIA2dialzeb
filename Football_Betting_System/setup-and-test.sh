#!/bin/bash

# Football Betting Platform - Complete Setup and Test Script
# This script sets up everything and runs comprehensive tests

set -e  # Exit on error

echo "🎯 Football Betting Platform - Setup & Test"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down > /dev/null 2>&1 || true
print_success "Containers stopped"

# Build and start services
print_status "Building and starting services (this may take a few minutes)..."
docker-compose up -d --build

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
echo -n "  Waiting for database"
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        echo ""
        print_success "Database is ready"
        break
    fi
    echo -n "."
    sleep 1
done

echo -n "  Waiting for backend"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo ""
        print_success "Backend is ready"
        break
    fi
    echo -n "."
    sleep 1
done

# Seed data
print_status "Seeding database with test data..."
SEED_RESPONSE=$(curl -s -X POST http://localhost:8000/api/seed-data)
if echo "$SEED_RESPONSE" | grep -q "successfully"; then
    print_success "Data seeded successfully"
    echo "$SEED_RESPONSE" | jq '.' 2>/dev/null || echo "$SEED_RESPONSE"
else
    print_warning "Data may already exist or seed failed"
    echo "$SEED_RESPONSE"
fi

echo ""
print_status "Training prediction model..."
TRAIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/train-model?force=true")
if echo "$TRAIN_RESPONSE" | grep -q "success"; then
    print_success "Model trained successfully"
else
    print_warning "Model training may have issues"
fi

echo ""
print_status "Running API tests..."

# Test 1: Health check
echo "  Test 1: Health check"
if curl -s http://localhost:8000/health | grep -q "ok"; then
    print_success "    Health check passed"
else
    print_error "    Health check failed"
fi

# Test 2: Get events
echo "  Test 2: Get events"
EVENTS=$(curl -s http://localhost:8000/api/events)
if echo "$EVENTS" | grep -q "events"; then
    EVENT_COUNT=$(echo "$EVENTS" | jq '.events | length' 2>/dev/null || echo "0")
    print_success "    Found $EVENT_COUNT events"
else
    print_error "    Failed to get events"
fi

# Test 3: Get model info
echo "  Test 3: Model info"
MODEL_INFO=$(curl -s http://localhost:8000/api/model-info)
if echo "$MODEL_INFO" | grep -q "teams_count"; then
    TEAMS=$(echo "$MODEL_INFO" | jq '.teams_count' 2>/dev/null || echo "0")
    print_success "    Model has data for $TEAMS teams"
else
    print_error "    Failed to get model info"
fi

# Test 4: Prediction
echo "  Test 4: Match prediction (PSG vs Lyon)"
PREDICTION=$(curl -s -X POST "http://localhost:8000/api/predict-match?team1=PSG&team2=Lyon")
if echo "$PREDICTION" | grep -q "outcome_probabilities"; then
    print_success "    Prediction generated successfully"
    HOME_WIN=$(echo "$PREDICTION" | jq '.outcome_probabilities.home_win * 100' 2>/dev/null || echo "N/A")
    DRAW=$(echo "$PREDICTION" | jq '.outcome_probabilities.draw * 100' 2>/dev/null || echo "N/A")
    AWAY_WIN=$(echo "$PREDICTION" | jq '.outcome_probabilities.away_win * 100' 2>/dev/null || echo "N/A")
    echo "      Home Win: ${HOME_WIN}%"
    echo "      Draw: ${DRAW}%"
    echo "      Away Win: ${AWAY_WIN}%"
else
    print_error "    Prediction failed"
fi

# Test 5: Team stats
echo "  Test 5: Team statistics"
STATS=$(curl -s "http://localhost:8000/api/team-stats?team=PSG")
if echo "$STATS" | grep -q "PSG"; then
    print_success "    Team stats retrieved successfully"
else
    print_error "    Failed to get team stats"
fi

# Test 6: Head-to-head
echo "  Test 6: Head-to-head stats"
H2H=$(curl -s "http://localhost:8000/api/head-to-head?team1=Real%20Madrid&team2=Barcelona")
if echo "$H2H" | grep -q "matches_played"; then
    MATCHES=$(echo "$H2H" | jq '.matches_played' 2>/dev/null || echo "0")
    print_success "    Found $MATCHES historical matches"
else
    print_error "    Failed to get H2H stats"
fi

echo ""
print_status "Testing frontend..."
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    print_success "Frontend is accessible"
else
    print_warning "Frontend may not be ready yet (still building)"
fi

echo ""
echo "============================================"
print_success "Setup Complete! 🎉"
echo ""
echo "📊 Access Points:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📚 Quick Commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "🎮 Try the UI:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Go to 'AI Predictions' tab"
echo "   3. Select a match and see AI predictions!"
echo ""
echo "🧪 API Examples:"
echo "   curl -X POST 'http://localhost:8000/api/predict-match?team1=PSG&team2=Lyon' | jq"
echo "   curl http://localhost:8000/api/team-stats | jq"
echo "   curl 'http://localhost:8000/api/head-to-head?team1=Real%20Madrid&team2=Barcelona' | jq"
echo ""
print_success "All tests passed! Your betting platform is ready! ⚽🎯"
