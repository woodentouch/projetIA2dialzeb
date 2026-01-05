import { useState, useEffect } from 'react';
import { Card, Title, Text, Button, Select, NumberInput, Group, Stack, Grid, GridCol, Badge, Loader, Alert, Modal } from './CustomComponents';
import { IconCash, IconTrophy, IconChartBar, IconWallet, IconAlertCircle } from '@tabler/icons-react';
import axios from 'axios';
import { safeNumber, safeMultiply, safeGet } from '../utils';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function BettingDashboard() {
  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [betType, setBetType] = useState('team1');
  const [betAmount, setBetAmount] = useState(10);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: 'success'|'error', message: string }

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    setEventsLoading(true);
    setEventsError(null);
    try {
      const response = await axios.get(`${API_BASE}/api/events`);
      setEvents(safeGet(response, 'data.events', []));
    } catch (err) {
      console.error('Failed to load events:', err);
      setEventsError('Failed to load events. Please try again.');
    } finally {
      setEventsLoading(false);
    }
  };

  const placeBet = async () => {
    if (!selectedEventId || !betType || betAmount <= 0) {
      setFeedback({ type: 'error', message: 'Please select a match, outcome, and amount.' });
      return;
    }

    const event = events.find(e => safeGet(e, 'id') === Number(selectedEventId));
    if (!event) return;

    const odds = betType === 'team1' ? safeGet(event, 'odds_team1', 1) :
                 betType === 'draw' ? safeGet(event, 'odds_draw', 1) :
                 safeGet(event, 'odds_team2', 1);

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/bets`, {
        event_id: Number(selectedEventId),
        bet_type: betType,
        amount: Number(betAmount),
        odds: Number(odds),
        user_id: 1
      });

      setFeedback({
        type: 'success',
        message: `Bet placed! Potential win: €${safeMultiply(betAmount, odds)}`,
      });

      setBetAmount(10);
      setSelectedEventId(null);
      setBetType('team1');
    } catch (err) {
      console.error('Failed to place bet:', err);
      setFeedback({ type: 'error', message: 'Failed to place bet. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const selectedEvent = events.find(e => safeGet(e, 'id') === Number(selectedEventId));
  const currentOdds = selectedEvent ? (
    betType === 'team1' ? safeGet(selectedEvent, 'odds_team1', 1) :
    betType === 'draw' ? safeGet(selectedEvent, 'odds_draw', 1) :
    safeGet(selectedEvent, 'odds_team2', 1)
  ) : 0;

  const potentialWin = safeMultiply(betAmount, currentOdds);

  return (
    <Stack gap="xxl">
      <Card 
        shadow="sm" 
        padding="xl" 
        radius="xl" 
        withBorder
        style={{
          background: 'rgba(30, 41, 59, 0.7)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderLeft: '6px solid #48bb78'
        }}
      >
        <Group justify="space-between">
          <div>
            <Title order={2} style={{ color: '#fff', fontWeight: 800 }}>💰 Betting Arena</Title>
            <Text c="dimmed" size="sm" mt={4}>Place your wagers and track your potential winnings</Text>
          </div>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(72, 187, 120, 0.15)',
              border: '1px solid rgba(72, 187, 120, 0.35)',
            }}
          >
            <IconWallet size={28} color="#48bb78" />
          </div>
        </Group>
      </Card>

      {feedback && (
        <Alert
          icon={<IconAlertCircle size={16} />}
          title={feedback.type === 'success' ? 'Success' : 'Error'}
          color={feedback.type === 'success' ? 'green' : 'red'}
        >
          {feedback.message}
        </Alert>
      )}

      {eventsError && (
        <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
          {eventsError}
        </Alert>
      )}

      <Grid gutter="xl">
        <Grid.Col span={{ base: 12, md: 7 }}>
          <Card shadow="lg" padding="xl" radius="lg" withBorder style={{ height: '100%', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid rgba(255,255,255,0.1)' }}>
            <Stack gap="xl">
              <Select
                label={<Text fw={600} size="sm" mb={4} c="dimmed">Select Match</Text>}
                placeholder="Choose a match to bet on"
                value={selectedEventId ? String(selectedEventId) : null}
                onChange={(val) => setSelectedEventId(val)}
                data={events.map(e => ({
                  value: String(safeGet(e, 'id', '')),
                  label: `${safeGet(e, 'team1', 'Team 1')} vs ${safeGet(e, 'team2', 'Team 2')}`
                }))}
                size="lg"
                radius="md"
                searchable
                maxDropdownHeight={280}
                disabled={eventsLoading}
                styles={{
                  input: {
                    background: 'rgba(0, 0, 0, 0.2)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: 'white',
                  },
                  dropdown: {
                    background: '#1a202c',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: 'white',
                  },
                  option: {
                    color: 'white',
                    '&:hover': {
                      background: 'rgba(255, 255, 255, 0.1)',
                    }
                  }
                }}
              />

              {eventsLoading && (
                <Group justify="center" py="md">
                  <Loader size="sm" />
                  <Text size="sm" c="dimmed">Loading events…</Text>
                </Group>
              )}

              {selectedEvent && (
                <Card shadow="sm" padding="md" radius="md" withBorder style={{ background: 'rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <Group justify="center" gap="xl" mb="md">
                    <Text size="xl" fw={800} c="white">{safeGet(selectedEvent, 'team1')}</Text>
                    <Badge size="lg" variant="outline" color="gray">VS</Badge>
                    <Text size="xl" fw={800} c="white">{safeGet(selectedEvent, 'team2')}</Text>
                  </Group>

                  <div style={{
                    height: 1,
                    background: 'rgba(255,255,255,0.1)',
                    margin: '16px 0',
                  }} />
                  
                  <Group grow gap="md">
                    <Button 
                      variant={betType === 'team1' ? 'gradient' : 'outline'} 
                      gradient={{ from: 'teal', to: 'green', deg: 105 }}
                      color="green" 
                      size="lg"
                      onClick={() => setBetType('team1')}
                      style={{ height: 70, border: betType !== 'team1' ? '1px solid rgba(255,255,255,0.2)' : 'none' }}
                    >
                      <Stack gap={2}>
                        <Text size="xs" fw={500} c={betType === 'team1' ? 'white' : 'dimmed'}>{safeGet(selectedEvent, 'team1')}</Text>
                        <Text size="xl" fw={900} c={betType === 'team1' ? 'white' : 'green'}>{safeNumber(safeGet(selectedEvent, 'odds_team1', 0))}</Text>
                      </Stack>
                    </Button>
                    <Button 
                      variant={betType === 'draw' ? 'gradient' : 'outline'} 
                      gradient={{ from: 'gray', to: 'dark', deg: 105 }}
                      color="gray" 
                      size="lg"
                      onClick={() => setBetType('draw')}
                      style={{ height: 70, border: betType !== 'draw' ? '1px solid rgba(255,255,255,0.2)' : 'none' }}
                    >
                      <Stack gap={2}>
                        <Text size="xs" fw={500} c={betType === 'draw' ? 'white' : 'dimmed'}>Draw</Text>
                        <Text size="xl" fw={900} c={betType === 'draw' ? 'white' : 'gray'}>{safeNumber(safeGet(selectedEvent, 'odds_draw', 0))}</Text>
                      </Stack>
                    </Button>
                    <Button 
                      variant={betType === 'team2' ? 'gradient' : 'outline'} 
                      gradient={{ from: 'blue', to: 'cyan', deg: 105 }}
                      color="blue" 
                      size="lg"
                      onClick={() => setBetType('team2')}
                      style={{ height: 70, border: betType !== 'team2' ? '1px solid rgba(255,255,255,0.2)' : 'none' }}
                    >
                      <Stack gap={2}>
                        <Text size="xs" fw={500} c={betType === 'team2' ? 'white' : 'dimmed'}>{safeGet(selectedEvent, 'team2')}</Text>
                        <Text size="xl" fw={900} c={betType === 'team2' ? 'white' : 'blue'}>{safeNumber(safeGet(selectedEvent, 'odds_team2', 0))}</Text>
                      </Stack>
                    </Button>
                  </Group>
                </Card>
              )}
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 5 }}>
          <Card 
            shadow="xl" 
            padding="xl" 
            radius="lg" 
            withBorder
            style={{ 
              background: 'linear-gradient(135deg, #2d3748 0%, #1a202c 100%)',
              color: 'white',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <Group justify="space-between" mb="xl">
                <Title order={3} style={{ color: 'white' }}>Bet Slip</Title>
                <IconCash size={24} color="#48bb78" />
              </Group>

              <Stack gap="xl">
                <div>
                  <Text size="sm" c="dimmed" mb={4}>Wager Amount (€)</Text>
                  <NumberInput
                    value={betAmount}
                    onChange={setBetAmount}
                    min={1}
                    size="xl"
                    radius="md"
                    prefix="€ "
                    styles={{
                      input: { fontWeight: 700, fontSize: 24 }
                    }}
                  />
                </div>

                <div style={{ padding: 16, borderRadius: 12, background: 'rgba(255,255,255,0.1)' }}>
                  <Group justify="space-between" mb="xs">
                    <Text c="dimmed">Odds:</Text>
                    <Text fw={700} c="white">{safeNumber(currentOdds)}</Text>
                  </Group>
                  <div style={{ height: 1, background: 'rgba(255,255,255,0.2)', margin: '10px 0' }} />
                  <Group justify="space-between">
                    <Text size="lg" fw={600} color="#48bb78">Potential Win:</Text>
                    <Text size="xl" fw={900} color="#48bb78">€{safeNumber(potentialWin)}</Text>
                  </Group>
                </div>
              </Stack>
            </div>

            <Button 
              fullWidth 
              size="xl" 
              color="green" 
              mt="xl"
              onClick={placeBet}
              loading={loading}
              disabled={!selectedEventId}
              className="lift-button"
              style={{
                height: 60,
                fontSize: 20,
                boxShadow: '0 4px 14px 0 rgba(72, 187, 120, 0.39)',
              }}
            >
              Place Bet
            </Button>
          </Card>
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
