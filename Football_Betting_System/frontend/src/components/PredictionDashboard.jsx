import { useEffect, useState } from 'react';
import { Card, Title, Text, Button, Select, Stack, Grid, GridCol, Group, Badge, Loader, Alert, Box } from './CustomComponents';
import { IconTrophy, IconAlertCircle } from '@tabler/icons-react';
import axios from 'axios';
import { safeNumber, safePercent, safeGet } from '../utils';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TEAMS = [
  "AC Milan", "Arsenal", "Aston Villa", "Atalanta", "Athletic Bilbao", "Atletico Madrid",
  "Augsburg", "Barcelona", "Bayer Leverkusen", "Bayern Munich", "Bologna", "Borussia Dortmund",
  "Borussia Monchengladbach", "Bournemouth", "Brentford", "Brighton", "Chelsea", "Crystal Palace",
  "Eintracht Frankfurt", "Everton", "Fiorentina", "Freiburg", "Fulham", "Getafe", "Girona",
  "Hoffenheim", "Inter Milan", "Juventus", "Lazio", "Leicester", "Lens", "Lille", "Liverpool",
  "Luton Town", "Lyon", "Mainz", "Mallorca", "Manchester City", "Manchester United", "Marseille",
  "Monaco", "Montpellier", "Monza", "Nantes", "Napoli", "Newcastle", "Nice", "Nottingham Forest",
  "Osasuna", "PSG", "RB Leipzig", "Real Betis", "Real Madrid", "Real Sociedad", "Reims", "Rennes",
  "Roma", "Salernitana", "Sevilla", "Southampton", "Strasbourg", "Torino", "Tottenham", "Union Berlin",
  "Valencia", "Villarreal", "West Ham", "Wolfsburg", "Wolves"
];

export default function PredictionDashboard({ initialTeam1 = '', initialTeam2 = '' }) {
  const [team1, setTeam1] = useState((initialTeam1 || '').trim());
  const [team2, setTeam2] = useState((initialTeam2 || '').trim());
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const t1 = (initialTeam1 || '').trim();
    const t2 = (initialTeam2 || '').trim();
    if (!t1 && !t2) return;

    setTeam1(t1);
    setTeam2(t2);
    setError(null);
    setPrediction(null);
  }, [initialTeam1, initialTeam2]);

  const predictMatch = async () => {
    if (!team1 || !team2) {
      setError('Please select both teams');
      return;
    }

    if (team1 === team2) {
      setError('Please select different teams');
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const url = `${API_BASE}/api/predict-match?team1=${encodeURIComponent(team1)}&team2=${encodeURIComponent(team2)}`;
      const response = await axios.get(url);
      setPrediction(response.data);
    } catch (err) {
      console.error('Prediction error:', err);
      setError(safeGet(err, 'response.data.detail', 'Failed to get prediction. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack gap="xxl">
      <Card 
        shadow="lg" 
        padding="xl" 
        radius="xl" 
        withBorder
        className="lift-card"
        style={{
          borderColor: 'rgba(102, 126, 234, 0.4)',
          borderWidth: 1,
          background: 'rgba(30, 41, 59, 0.7)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <Group justify="space-between" mb="md">
          <Title order={2} style={{ color: '#a3bffa', fontSize: 32, fontWeight: 900 }}>
            🎯 AI Prediction Engine
          </Title>
          <Badge 
            size="lg" 
            variant="gradient" 
            gradient={{ from: '#667eea', to: '#764ba2' }}
            style={{ fontSize: 14, padding: '10px 16px' }}
          >
            Bayesian AI
          </Badge>
        </Group>
        <Text c="dimmed" mb="xl" size="md">
          Powered by Monte Carlo Simulation with 10,000+ iterations
        </Text>
        <Grid gutter="xl" style={{ alignItems: 'end', marginBottom: '32px' }}>
          <Grid.Col span={{ base: 12, md: 5 }}>
            <Select
              label={<Text fw={600} size="sm" c="dimmed" mb={4}>🏠 Home Team</Text>}
              placeholder="Select home team"
              value={team1}
              onChange={setTeam1}
              data={TEAMS}
              searchable
              size="lg"
              radius="md"
              styles={{
                input: { 
                  fontSize: 16, 
                  padding: '12px 16px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  color: 'white',
                },
                dropdown: {
                  background: '#1a202c',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  color: 'white',
                },
                option: {
                  color: 'white',
                  '&:hover': {
                    background: 'rgba(102, 126, 234, 0.2)',
                  }
                }
              }}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 2 }} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', paddingBottom: '4px' }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 15px rgba(118, 75, 162, 0.4)',
              }}
            >
              <Text fw={900} size="lg" c="white">VS</Text>
            </div>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 5 }}>
            <Select
              label={<Text fw={600} size="sm" c="dimmed" mb={4}>✈️ Away Team</Text>}
              placeholder="Select away team"
              value={team2}
              onChange={setTeam2}
              data={TEAMS}
              searchable
              size="lg"
              radius="md"
              styles={{
                input: { 
                  fontSize: 16, 
                  padding: '12px 16px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  color: 'white',
                },
                dropdown: {
                  background: '#1a202c',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  color: 'white',
                },
                option: {
                  color: 'white',
                  '&:hover': {
                    background: 'rgba(102, 126, 234, 0.2)',
                  }
                }
              }}
            />
          </Grid.Col>
        </Grid>
        <Button 
          fullWidth 
          mt="xl" 
          size="xl" 
          onClick={predictMatch}
          leftSection={<IconTrophy size={24} />}
          disabled={!team1 || !team2 || team1 === team2}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
            fontSize: 20,
            fontWeight: 700,
            height: 65,
            borderRadius: 12,
            transition: 'all 0.3s ease',
            border: 'none',
            boxShadow: '0 8px 25px rgba(102, 126, 234, 0.4)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-3px)';
            e.currentTarget.style.boxShadow = '0 12px 35px rgba(102, 126, 234, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'none';
            e.currentTarget.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.4)';
          }}
        >
          🚀 Predict Match with AI
        </Button>
      </Card>

      {error && (
        <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
          {error}
        </Alert>
      )}

      {loading && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group justify="center" py="xl">
            <Loader size="xl" />
            <Text>Calculating predictions with Bayesian inference...</Text>
          </Group>
        </Card>
      )}

      {prediction && !loading && (
        <>
          <Card 
            shadow="xl" 
            padding="xl" 
            radius="xl" 
            withBorder
            style={{
              background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(102, 126, 234, 0.08) 100%)',
              borderColor: 'rgba(102, 126, 234, 0.4)',
              borderWidth: 2,
            }}
          >
            <Group justify="center" mb="md">
              <Badge 
                size="xl" 
                variant="gradient" 
                gradient={{ from: 'indigo', to: 'cyan' }}
                style={{ fontSize: 16, padding: '15px 20px' }}
              >
                {safeGet(prediction, 'league', 'Unknown League')}
              </Badge>
              <Badge 
                size="xl" 
                variant="gradient" 
                gradient={{ from: 'orange', to: 'red' }}
                style={{ fontSize: 16, padding: '15px 20px' }}
              >
                AI Confidence: {safePercent(safeGet(prediction, 'confidence', 0))}
              </Badge>
            </Group>
            <Title order={3} mb="xl" ta="center" style={{ color: '#667eea', fontSize: 28, fontWeight: 900 }}>
              📊 Match Outcome Probabilities
            </Title>
            <Grid>
              <Grid.Col span={{ base: 12, md: 4 }}>
                <Card 
                  padding="xl" 
                  withBorder 
                  radius="lg"
                  className="lift-card"
                  style={{ 
                    background: 'linear-gradient(135deg, #4caf50 0%, #66bb6a 100%)',
                    border: 'none',
                    textAlign: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <Text size="md" fw={700} mb="md" style={{ color: 'white', opacity: 0.9 }}>
                    🏆 {team1} Win
                  </Text>
                  <Text size={48} fw={900} style={{ color: 'white', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                    {safePercent(safeGet(prediction, 'outcome_probabilities.home_win', 0))}
                  </Text>
                </Card>
              </Grid.Col>
              <Grid.Col span={{ base: 12, md: 4 }}>
                <Card 
                  padding="xl" 
                  withBorder 
                  radius="lg"
                  className="lift-card"
                  style={{ 
                    background: 'linear-gradient(135deg, #ff9800 0%, #ffa726 100%)',
                    border: 'none',
                    textAlign: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <Text size="md" fw={700} mb="md" style={{ color: 'white', opacity: 0.9 }}>
                    🤝 Draw
                  </Text>
                  <Text size={48} fw={900} style={{ color: 'white', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                    {safePercent(safeGet(prediction, 'outcome_probabilities.draw', 0))}
                  </Text>
                </Card>
              </Grid.Col>
              <Grid.Col span={{ base: 12, md: 4 }}>
                <Card 
                  padding="xl" 
                  withBorder 
                  radius="lg"
                  className="lift-card"
                  style={{ 
                    background: 'linear-gradient(135deg, #2196f3 0%, #42a5f5 100%)',
                    border: 'none',
                    textAlign: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <Text size="md" fw={700} mb="md" style={{ color: 'white', opacity: 0.9 }}>
                    🎯 {team2} Win
                  </Text>
                  <Text size={48} fw={900} style={{ color: 'white', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                    {safePercent(safeGet(prediction, 'outcome_probabilities.away_win', 0))}
                  </Text>
                </Card>
              </Grid.Col>
            </Grid>
          </Card>

          <Card shadow="lg" padding="xl" radius="md" withBorder>
            <Title order={3} mb="xl" ta="center" style={{ color: '#667eea' }}>
              💰 Fair Betting Odds
            </Title>
            <Grid>
              <Grid.Col span={{ base: 12, md: 4 }}>
                <Text ta="center" size="sm" mb="xs">{team1} Win</Text>
                <Badge size="xl" color="green" variant="filled" fullWidth>
                  {safeNumber(safeGet(prediction, 'betting_odds.home_odds', 0))}
                </Badge>
              </Grid.Col>
              <Grid.Col span={{ base: 12, md: 4 }}>
                <Text ta="center" size="sm" mb="xs">Draw</Text>
                <Badge size="xl" color="yellow" variant="filled" fullWidth>
                  {safeNumber(safeGet(prediction, 'betting_odds.draw_odds', 0))}
                </Badge>
              </Grid.Col>
              <Grid.Col span={{ base: 12, md: 4 }}>
                <Text ta="center" size="sm" mb="xs">{team2} Win</Text>
                <Badge size="xl" color="blue" variant="filled" fullWidth>
                  {safeNumber(safeGet(prediction, 'betting_odds.away_odds', 0))}
                </Badge>
              </Grid.Col>
            </Grid>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">Expected Goals</Title>
            <Grid>
              <Grid.Col span={{ base: 12, md: 6 }}>
                <Text size="sm" c="dimmed">{team1} Expected Goals</Text>
                <Text size="xl" fw={700}>
                  {safeNumber(safeGet(prediction, 'goals_prediction.expected_home_goals', 0))}
                </Text>
              </Grid.Col>
              <Grid.Col span={{ base: 12, md: 6 }}>
                <Text size="sm" c="dimmed">{team2} Expected Goals</Text>
                <Text size="xl" fw={700}>
                  {safeNumber(safeGet(prediction, 'goals_prediction.expected_away_goals', 0))}
                </Text>
              </Grid.Col>
              <Grid.Col span={12}>
                <Text size="sm" c="dimmed">Total Expected Goals</Text>
                <Text size="xl" fw={700} color="blue">
                  {safeNumber(safeGet(prediction, 'goals_prediction.expected_total_goals', 0))}
                </Text>
              </Grid.Col>
            </Grid>
          </Card>

          {safeGet(prediction, 'most_likely_scores') && (
            <Card shadow="sm" padding="lg" radius="md" withBorder>
              <Title order={3} mb="md">Most Likely Scores</Title>
              <Grid>
                {safeGet(prediction, 'most_likely_scores', []).slice(0, 5).map((score, idx) => (
                  <Grid.Col key={idx} span={{ base: 12, md: 6 }}>
                    <Group justify="space-between">
                      <Text fw={500}>{safeGet(score, 'score', 'N/A')}</Text>
                      <Badge>{safePercent(safeGet(score, 'probability', 0))}</Badge>
                    </Group>
                  </Grid.Col>
                ))}
              </Grid>
            </Card>
          )}

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">Additional Stats</Title>
            <Stack gap="xs">
              <Group justify="space-between">
                <Text>Over 2.5 Goals</Text>
                <Badge size="lg">{safePercent(safeGet(prediction, 'over_under.over_2.5', 0))}</Badge>
              </Group>
              <Group justify="space-between">
                <Text>Both Teams Score</Text>
                <Badge size="lg">{safePercent(safeGet(prediction, 'both_teams_score', 0))}</Badge>
              </Group>
              <Group justify="space-between">
                <Text>Confidence Level</Text>
                <Badge size="lg" color={safeGet(prediction, 'confidence', 0) > 0.3 ? 'green' : 'yellow'}>
                  {safePercent(safeGet(prediction, 'confidence', 0))}
                </Badge>
              </Group>
            </Stack>
          </Card>

          {safeGet(prediction, 'recommendation') && (
            <Alert color="blue" title="Recommendation">
              {safeGet(prediction, 'recommendation', 'No recommendation available')}
            </Alert>
          )}
        </>
      )}
    </Stack>
  );
}
