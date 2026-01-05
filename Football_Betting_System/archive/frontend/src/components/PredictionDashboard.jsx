import { useState, useEffect } from 'react';
import { IconAlertCircle, IconChartBar, IconTrophy, IconBrain, IconRefresh } from '@tabler/icons-react';
import axios from 'axios';
import { Card, Title, Text, Badge, Progress, Group, Stack, Button, Select, Grid, GridCol, Loader, Alert } from './CustomComponents';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function PredictionDashboard() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    loadEvents();
    loadModelInfo();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/events`);
      setEvents(response.data.events || []);
    } catch (err) {
      console.error('Failed to load events:', err);
    }
  };

  const loadModelInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/model-info`);
      setModelInfo(response.data);
    } catch (err) {
      console.error('Failed to load model info:', err);
    }
  };

  const loadPrediction = async (team1, team2) => {
    setLoading(true);
    setError(null);
    setPrediction(null); // Clear previous prediction
    
    try {
      console.log('🔍 Loading prediction for:', team1, 'vs', team2);
      const response = await axios.post(
        `${API_BASE}/api/predict-match?team1=${encodeURIComponent(team1)}&team2=${encodeURIComponent(team2)}`
      );
      
      console.log('✅ Raw response:', response.data);
      
      // Validate the response has all required fields
      const data = response.data;
      if (!data || !data.outcome_probabilities || !data.betting_odds || !data.goals_prediction) {
        console.error('❌ Missing fields in response:', {
          hasData: !!data,
          hasOutcome: !!data?.outcome_probabilities,
          hasBetting: !!data?.betting_odds,
          hasGoals: !!data?.goals_prediction
        });
        throw new Error('Invalid prediction data received');
      }
      
      console.log('✅ Validation passed, setting prediction');
      setPrediction(data);
      setError(null);
    } catch (err) {
      console.error('❌ Prediction error:', err);
      console.error('❌ Error stack:', err.stack);
      setError(err.response?.data?.detail || err.message || 'Failed to load prediction');
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  const retrainModel = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/train-model?force=true`);
      await loadModelInfo();
      if (selectedEvent) {
        const event = events.find(e => e.id === parseInt(selectedEvent));
        if (event) {
          await loadPrediction(event.team1, event.team2);
        }
      }
    } catch (err) {
      setError('Failed to retrain model');
    } finally {
      setLoading(false);
    }
  };

  const handleEventChange = (eventId) => {
    if (!eventId) return;
    
    setSelectedEvent(eventId);
    const event = events.find(e => e.id === parseInt(eventId));
    if (event && event.team1 && event.team2) {
      loadPrediction(event.team1, event.team2);
    } else {
      setError('Invalid event selected');
    }
  };

  const getOutcomeColor = (outcome) => {
    const colors = {
      'Home Win': 'green',
      'Draw': 'yellow',
      'Away Win': 'blue'
    };
    return colors[outcome] || 'gray';
  };

  const formatPercentage = (value) => {
    if (value === undefined || value === null || isNaN(value)) return '0.0';
    const num = Number(value);
    if (isNaN(num) || !isFinite(num)) return '0.0';
    return (num * 100).toFixed(1);
  };

  const safeToFixed = (value, decimals = 2) => {
    if (value === undefined || value === null || isNaN(value)) return 'N/A';
    const num = Number(value);
    if (isNaN(num) || !isFinite(num)) return 'N/A';
    return num.toFixed(decimals);
  };

  return (
    <Stack spacing="md">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group position="apart" mb="md">
          <div>
            <Title order={2}>⚽ AI Match Predictions</Title>
            <Text size="sm" color="dimmed">
              Advanced Bayesian football prediction system
            </Text>
          </div>
          <Group>
            {modelInfo && (
              <Badge variant="dot" size="lg">
                {modelInfo.teams_count} teams trained
              </Badge>
            )}
            <Button
              leftIcon={<IconRefresh size={16} />}
              variant="light"
              onClick={retrainModel}
              loading={loading}
            >
              Retrain Model
            </Button>
          </Group>
        </Group>

        <Select
          label="Select Match to Predict"
          placeholder="Choose an event"
          value={selectedEvent}
          onChange={handleEventChange}
          data={events.map(event => ({
            value: event.id.toString(),
            label: `${event.team1} vs ${event.team2} - ${new Date(event.date).toLocaleDateString()}`
          }))}
          size="md"
          mb="md"
        />
      </Card>

      {error && (
        <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
          {error}
        </Alert>
      )}

      {loading && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group position="center" py="xl">
            <Loader size="xl" />
            <Text>Calculating predictions...</Text>
          </Group>
        </Card>
      )}

      {prediction && !loading && prediction.outcome_probabilities && (
        <>
          {console.log('🎨 Rendering prediction:', prediction)}
          {/* Main Prediction Card */}
          <Card shadow="lg" padding="xl" radius="lg" withBorder style={{ background: 'linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)' }}>
            <Stack spacing="lg">
              {/* Match Header */}
              <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                <Badge color="gray" variant="outline" size="lg" style={{ marginBottom: '10px' }}>
                  {prediction.league || 'Unknown League'}
                </Badge>
                <Grid align="center" justify="center">
                  <GridCol span={5}>
                    <Title order={2} style={{ color: '#fff' }}>{prediction?.team1}</Title>
                    <Text size="sm" color="dimmed">Home</Text>
                  </GridCol>
                  <GridCol span={2}>
                    <Badge size="xl" color="red" variant="filled" style={{ fontSize: '1.5rem', padding: '10px 20px' }}>VS</Badge>
                  </GridCol>
                  <GridCol span={5}>
                    <Title order={2} style={{ color: '#fff' }}>{prediction?.team2}</Title>
                    <Text size="sm" color="dimmed">Away</Text>
                  </GridCol>
                </Grid>
              </div>

              <Group position="center">
                <Badge color={prediction.confidence > 0.7 ? 'green' : 'yellow'} size="lg" variant="light">
                  AI Confidence: {formatPercentage(prediction?.confidence)}%
                </Badge>
                {prediction?.from_cache && (
                  <Badge color="gray" variant="outline">
                    Cached
                  </Badge>
                )}
              </Group>

              <Alert icon={<IconBrain size={20} />} color="blue" title="AI Analysis" style={{ background: 'rgba(33, 150, 243, 0.1)' }}>
                <Text size="lg" weight={500}>{prediction?.recommendation}</Text>
              </Alert>
            </Stack>
          </Card>

          {/* Betting Odds & Probabilities */}
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={3} mb="lg" align="center">Match Probabilities & Odds</Title>
            <Grid gutter="xl">
              {/* Home Win */}
              <GridCol span={4}>
                <Card padding="md" withBorder style={{ borderColor: 'rgba(76, 175, 80, 0.3)', background: 'rgba(76, 175, 80, 0.05)' }}>
                  <Text align="center" size="md" weight={600} color="green" style={{ textTransform: 'uppercase', letterSpacing: '1px' }}>
                    {prediction?.team1} Win
                  </Text>
                  <Text align="center" size="xl" weight={800} style={{ fontSize: '2.5rem', margin: '10px 0' }}>
                    {formatPercentage(prediction.outcome_probabilities?.home_win)}%
                  </Text>
                  <div style={{ background: 'rgba(255,255,255,0.1)', padding: '8px', borderRadius: '8px', textAlign: 'center' }}>
                    <Text size="sm" color="dimmed">Implied Odds</Text>
                    <Text size="xl" weight={700} color="white">{safeToFixed(prediction.betting_odds?.home_odds)}</Text>
                  </div>
                </Card>
              </GridCol>

              {/* Draw */}
              <GridCol span={4}>
                <Card padding="md" withBorder style={{ borderColor: 'rgba(255, 193, 7, 0.3)', background: 'rgba(255, 193, 7, 0.05)' }}>
                  <Text align="center" size="md" weight={600} color="yellow" style={{ textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Draw
                  </Text>
                  <Text align="center" size="xl" weight={800} style={{ fontSize: '2.5rem', margin: '10px 0' }}>
                    {formatPercentage(prediction.outcome_probabilities?.draw)}%
                  </Text>
                  <div style={{ background: 'rgba(255,255,255,0.1)', padding: '8px', borderRadius: '8px', textAlign: 'center' }}>
                    <Text size="sm" color="dimmed">Implied Odds</Text>
                    <Text size="xl" weight={700} color="white">{safeToFixed(prediction.betting_odds?.draw_odds)}</Text>
                  </div>
                </Card>
              </GridCol>

              {/* Away Win */}
              <GridCol span={4}>
                <Card padding="md" withBorder style={{ borderColor: 'rgba(33, 150, 243, 0.3)', background: 'rgba(33, 150, 243, 0.05)' }}>
                  <Text align="center" size="md" weight={600} color="blue" style={{ textTransform: 'uppercase', letterSpacing: '1px' }}>
                    {prediction?.team2} Win
                  </Text>
                  <Text align="center" size="xl" weight={800} style={{ fontSize: '2.5rem', margin: '10px 0' }}>
                    {formatPercentage(prediction.outcome_probabilities?.away_win)}%
                  </Text>
                  <div style={{ background: 'rgba(255,255,255,0.1)', padding: '8px', borderRadius: '8px', textAlign: 'center' }}>
                    <Text size="sm" color="dimmed">Implied Odds</Text>
                    <Text size="xl" weight={700} color="white">{safeToFixed(prediction.betting_odds?.away_odds)}</Text>
                  </div>
                </Card>
              </GridCol>
            </Grid>
          </Card>

          {/* Goals Prediction */}
          <Grid>
            <GridCol span={6}>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Title order={4} mb="md">Expected Goals</Title>
                <Stack spacing="md">
                  <div>
                    <Group position="apart" mb="xs">
                      <Text weight={500}>{prediction?.team1 || 'Home'}</Text>
                      <Badge color="blue">
                        {safeToFixed(prediction.goals_prediction?.expected_home_goals)} goals
                      </Badge>
                    </Group>
                    <Text size="xs" color="dimmed">
                      Confidence interval: {safeToFixed(prediction.goals_prediction?.home_goals_ci?.[0], 1)} - {safeToFixed(prediction.goals_prediction?.home_goals_ci?.[1], 1)}
                    </Text>
                  </div>

                  <div>
                    <Group position="apart" mb="xs">
                      <Text weight={500}>{prediction?.team2 || 'Away'}</Text>
                      <Badge color="grape">
                        {safeToFixed(prediction.goals_prediction?.expected_away_goals)} goals
                      </Badge>
                    </Group>
                    <Text size="xs" color="dimmed">
                      Confidence interval: {safeToFixed(prediction.goals_prediction?.away_goals_ci?.[0], 1)} - {safeToFixed(prediction.goals_prediction?.away_goals_ci?.[1], 1)}
                    </Text>
                  </div>

                  <div>
                    <Group position="apart">
                      <Text weight={500}>Total Expected</Text>
                      <Badge color="teal" size="lg">
                        {safeToFixed(prediction.goals_prediction?.expected_total_goals)} goals
                      </Badge>
                    </Group>
                  </div>
                </Stack>
              </Card>
            </GridCol>

            <GridCol span={6}>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Title order={4} mb="md">Most Likely Scores</Title>
                <Stack spacing="xs">
                  {(prediction.most_likely_scores || []).slice(0, 5).map((score, idx) => (
                    <Group key={idx} position="apart">
                      <Group spacing="xs">
                        <Badge color={idx === 0 ? 'blue' : 'gray'} variant={idx === 0 ? 'filled' : 'outline'}>
                          #{idx + 1}
                        </Badge>
                        <Text weight={500} size="lg">
                          {score?.score || 'N/A'}
                        </Text>
                      </Group>
                      <div style={{ flex: 1, marginLeft: 16, marginRight: 16 }}>
                        <Progress
                          value={(score?.probability || 0) * 100}
                          color={idx === 0 ? 'blue' : 'gray'}
                          size="md"
                        />
                      </div>
                      <Text size="sm" weight={500}>
                        {formatPercentage(score?.probability)}%
                      </Text>
                    </Group>
                  ))}
                </Stack>
              </Card>
            </GridCol>
          </Grid>

          {/* Over/Under & Additional Stats */}
          <Grid>
            <GridCol span={6}>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Title order={4} mb="md">Over/Under Predictions</Title>
                <Stack spacing="sm">
                  <div>
                    <Group position="apart" mb="xs">
                      <Text>Over 1.5 Goals</Text>
                      <Badge color="green">
                        {formatPercentage(prediction.over_under?.['over_1.5'])}%
                      </Badge>
                    </Group>
                    <Progress
                      value={(prediction.over_under?.['over_1.5'] || 0) * 100}
                      color="green"
                      size="md"
                    />
                  </div>

                  <div>
                    <Group position="apart" mb="xs">
                      <Text>Over 2.5 Goals</Text>
                      <Badge color="yellow">
                        {formatPercentage(prediction.over_under?.['over_2.5'])}%
                      </Badge>
                    </Group>
                    <Progress
                      value={(prediction.over_under?.['over_2.5'] || 0) * 100}
                      color="yellow"
                      size="md"
                    />
                  </div>

                  <div>
                    <Group position="apart" mb="xs">
                      <Text>Over 3.5 Goals</Text>
                      <Badge color="orange">
                        {formatPercentage(prediction.over_under?.['over_3.5'])}%
                      </Badge>
                    </Group>
                    <Progress
                      value={(prediction.over_under?.['over_3.5'] || 0) * 100}
                      color="orange"
                      size="md"
                    />
                  </div>
                </Stack>
              </Card>
            </GridCol>

            <GridCol span={6}>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Title order={4} mb="md">Team Form & Stats</Title>
                <Stack spacing="md">
                  <div>
                    <Group position="apart" mb="xs">
                      <Text weight={500}>{prediction?.team1 || 'Home'} Form</Text>
                      <Badge color="blue">
                        {prediction.match_info?.team1_form || 'N/A'}
                      </Badge>
                    </Group>
                    {prediction.match_info?.team1_recent && (
                      <Group spacing="xs">
                        {(prediction.match_info?.team1_recent || []).map((result, idx) => (
                          <Badge
                            key={idx}
                            color={result === 'W' ? 'green' : result === 'D' ? 'yellow' : 'red'}
                            size="lg"
                          >
                            {result}
                          </Badge>
                        ))}
                      </Group>
                    )}
                  </div>

                  <div>
                    <Group position="apart" mb="xs">
                      <Text weight={500}>{prediction?.team2 || 'Away'} Form</Text>
                      <Badge color="grape">
                        {prediction.match_info?.team2_form || 'N/A'}
                      </Badge>
                    </Group>
                    {prediction.match_info?.team2_recent && (
                      <Group spacing="xs">
                        {(prediction.match_info?.team2_recent || []).map((result, idx) => (
                          <Badge
                            key={idx}
                            color={result === 'W' ? 'green' : result === 'D' ? 'yellow' : 'red'}
                            size="lg"
                          >
                            {result}
                          </Badge>
                        ))}
                      </Group>
                    )}
                  </div>

                  <div>
                    <Group position="apart">
                      <Text weight={500}>Both Teams to Score</Text>
                      <Badge color="teal" size="lg">
                        {formatPercentage(prediction?.both_teams_score)}%
                      </Badge>
                    </Group>
                  </div>

                  {prediction.match_info?.h2h_matches > 0 && (
                    <div>
                      <Group position="apart">
                        <Text weight={500}>Head-to-Head Matches</Text>
                        <Badge color="gray" size="lg">
                          {prediction.match_info?.h2h_matches || 0} matches
                        </Badge>
                      </Group>
                    </div>
                  )}
                </Stack>
              </Card>
            </GridCol>
          </Grid>
        </>
      )}
    </Stack>
  );
}
