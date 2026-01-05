import { useState, useEffect } from 'react';
import { IconCalendar, IconClock } from '@tabler/icons-react';
import axios from 'axios';
import { Card, Title, Text, Badge, Group, Stack, Grid, GridCol, Loader } from './CustomComponents';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const safeToFixed = (value, decimals = 2) => {
  if (value === undefined || value === null || isNaN(value)) return 'N/A';
  const num = Number(value);
  if (isNaN(num) || !isFinite(num)) return 'N/A';
  return num.toFixed(decimals);
};

export default function EventsList() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/events`);
      setEvents(response.data.events || []);
    } catch (err) {
      console.error('Failed to load events:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group position="center" py="xl">
          <Loader size="xl" />
        </Group>
      </Card>
    );
  }

  return (
    <Stack spacing="md">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={2} mb="md">Upcoming Football Events</Title>
        <Text color="dimmed">Browse all available matches</Text>
      </Card>

      <Grid>
        {events.map((event) => (
          <GridCol key={event?.id || Math.random()} span={12} md={6}>
            <Card shadow="md" padding="lg" radius="md" withBorder>
              <Stack spacing="md">
                <Group position="apart">
                  <Badge color="blue" variant="filled">
                    {event?.status?.toUpperCase() || 'UPCOMING'}
                  </Badge>
                  <Group spacing="xs">
                    <IconCalendar size={16} />
                    <Text size="sm">
                      {event?.date ? new Date(event.date).toLocaleDateString() : 'TBD'}
                    </Text>
                  </Group>
                </Group>

                <div>
                  <Group position="center" spacing="lg" mb="md">
                    <div style={{ textAlign: 'center' }}>
                      <Text size="xl" weight={700}>{event?.team1 || 'Team 1'}</Text>
                    </div>
                    <Text size="xl" weight={700} color="dimmed">VS</Text>
                    <div style={{ textAlign: 'center' }}>
                      <Text size="xl" weight={700}>{event?.team2 || 'Team 2'}</Text>
                    </div>
                  </Group>

                  <Group position="center" spacing="xs">
                    <IconClock size={16} />
                    <Text size="sm" color="dimmed">
                      {event?.date ? new Date(event.date).toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      }) : 'TBD'}
                    </Text>
                  </Group>
                </div>

                <div>
                  <Text size="sm" weight={600} mb="xs">Betting Odds</Text>
                  <Group position="apart">
                    <div style={{ textAlign: 'center' }}>
                      <Text size="xs" color="dimmed">Home Win</Text>
                      <Badge color="green" size="lg">
                        {safeToFixed(event?.odds_team1)}
                      </Badge>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <Text size="xs" color="dimmed">Draw</Text>
                      <Badge color="yellow" size="lg">
                        {safeToFixed(event?.odds_draw)}
                      </Badge>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <Text size="xs" color="dimmed">Away Win</Text>
                      <Badge color="blue" size="lg">
                        {safeToFixed(event?.odds_team2)}
                      </Badge>
                    </div>
                  </Group>
                </div>
              </Stack>
            </Card>
          </GridCol>
        ))}
      </Grid>

      {events.length === 0 && (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Text align="center" color="dimmed">
            No events available. Use the seed data endpoint to create test events.
          </Text>
        </Card>
      )}
    </Stack>
  );
}
