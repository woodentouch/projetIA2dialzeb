import { useState, useEffect } from 'react';
import { IconCash, IconTrophy } from '@tabler/icons-react';
import axios from 'axios';
import { Card, Title, Text, Button, Select, NumberInput, Modal, Group, Stack, Grid, GridCol, Badge, Loader } from './CustomComponents';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const safeToFixed = (value, decimals = 2) => {
  if (value === undefined || value === null || isNaN(value)) return 'N/A';
  const num = Number(value);
  if (isNaN(num) || !isFinite(num)) return 'N/A';
  return num.toFixed(decimals);
};

export default function BettingDashboard() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpened, setModalOpened] = useState(false);
  const [betAmount, setBetAmount] = useState(10);
  const [betType, setBetType] = useState('team1');

  useEffect(() => {
    loadEvents();
  }, []);

  useEffect(() => {
    if (selectedEvent) {
      loadPlayers(selectedEvent);
    }
  }, [selectedEvent]);

  const loadEvents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/events`);
      setEvents(response.data.events || []);
    } catch (err) {
      console.error('Failed to load events:', err);
    }
  };

  const loadPlayers = async (eventId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/events/${eventId}/players`);
      setPlayers(response.data || []);
    } catch (err) {
      console.error('Failed to load players:', err);
    } finally {
      setLoading(false);
    }
  };

  const placeBet = async () => {
    const event = events.find(e => e?.id === parseInt(selectedEvent));
    if (!event) return;

    const odds = betType === 'team1' ? (Number(event?.odds_team1) || 1.0) : 
                 betType === 'draw' ? (Number(event?.odds_draw) || 1.0) : (Number(event?.odds_team2) || 1.0);

    try {
      await axios.post(`${API_BASE}/api/bets`, {
        event_id: parseInt(selectedEvent),
        bet_type: betType,
        amount: betAmount,
        odds: odds,
        user_id: 1
      });

      notifications.show({
        title: 'Success!',
        message: `Bet placed successfully! Potential win: €${safeToFixed(betAmount * odds)}`,
        color: 'green',
      });

      setModalOpened(false);
    } catch (err) {
      notifications.show({
        title: 'Error',
        message: 'Failed to place bet',
        color: 'red',
      });
    }
  };

  const event = events.find(e => e?.id === parseInt(selectedEvent));

  return (
    <Stack spacing="md">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={2} mb="md">Place Your Bets</Title>
        <Select
          label="Select Event"
          placeholder="Choose a match"
          value={selectedEvent}
          onChange={setSelectedEvent}
          data={events.map(e => ({
            value: e?.id?.toString() || '',
            label: `${e?.team1 || 'Team 1'} vs ${e?.team2 || 'Team 2'}`
          }))}
        />
      </Card>

      {event && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group position="apart" mb="md">
            <Title order={3}>{event?.team1 || 'Team 1'} vs {event?.team2 || 'Team 2'}</Title>
            <Button onClick={() => setModalOpened(true)} leftIcon={<IconCash />}>
              Place Bet
            </Button>
          </Group>

          <Grid>
            <GridCol span={4}>
              <Card padding="sm" withBorder>
                <Text align="center" weight={500}>{event?.team1 || 'Team 1'} Win</Text>
                <Text align="center" size="xl" weight={700} color="green">
                  {safeToFixed(event?.odds_team1)}
                </Text>
              </Card>
            </GridCol>
            <GridCol span={4}>
              <Card padding="sm" withBorder>
                <Text align="center" weight={500}>Draw</Text>
                <Text align="center" size="xl" weight={700} color="yellow">
                  {safeToFixed(event?.odds_draw)}
                </Text>
              </Card>
            </GridCol>
            <GridCol span={4}>
              <Card padding="sm" withBorder>
                <Text align="center" weight={500}>{event?.team2 || 'Team 2'} Win</Text>
                <Text align="center" size="xl" weight={700} color="blue">
                  {safeToFixed(event?.odds_team2)}
                </Text>
              </Card>
            </GridCol>
          </Grid>
        </Card>
      )}

      {loading && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group position="center">
            <Loader />
          </Group>
        </Card>
      )}

      {players.length > 0 && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Title order={4} mb="md">Players</Title>
          <Grid>
            {players.map((player) => (
              <GridCol key={player?.id || Math.random()} span={12} sm={6} md={4}>
                <Card padding="sm" withBorder>
                  <Group mb="xs">
                    <Badge>{player?.number || 'N/A'}</Badge>
                    <Text weight={600}>{player?.name || 'Unknown'}</Text>
                  </Group>
                  <Text size="xs" color="dimmed" mb="xs">{player?.position || 'N/A'} - {player?.team || 'N/A'}</Text>
                  <Stack spacing={4}>
                    <Group position="apart">
                      <Text size="xs">Attack:</Text>
                      <Badge color="red" size="sm">{player?.attack || 0}</Badge>
                    </Group>
                    <Group position="apart">
                      <Text size="xs">Defense:</Text>
                      <Badge color="blue" size="sm">{player?.defense || 0}</Badge>
                    </Group>
                    <Group position="apart">
                      <Text size="xs">Speed:</Text>
                      <Badge color="green" size="sm">{player?.speed || 0}</Badge>
                    </Group>
                  </Stack>
                </Card>
              </GridCol>
            ))}
          </Grid>
        </Card>
      )}

      <Modal
        opened={modalOpened}
        onClose={() => setModalOpened(false)}
        title="Place Bet"
      >
        <Stack>
          <Select
            label="Bet Type"
            value={betType}
            onChange={setBetType}
            data={[
              { value: 'team1', label: `${event?.team1} Win` },
              { value: 'draw', label: 'Draw' },
              { value: 'team2', label: `${event?.team2} Win` },
            ]}
          />
          <NumberInput
            label="Amount (€)"
            value={betAmount}
            onChange={setBetAmount}
            min={1}
            max={10000}
          />
          <Text>
            Potential Win: €
            {event && betType ? safeToFixed(
              betAmount * (betType === 'team1' ? (Number(event?.odds_team1) || 1.0) : 
                            betType === 'draw' ? (Number(event?.odds_draw) || 1.0) : (Number(event?.odds_team2) || 1.0))
            ) : '0.00'}
          </Text>
          <Button onClick={placeBet} fullWidth>
            Confirm Bet
          </Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
