import { useState, useEffect } from 'react';
import { IconCalendar, IconClock, IconFlame, IconTrendingUp } from '@tabler/icons-react';
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
  const [filter, setFilter] = useState('all'); // all, today, upcoming

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

  const getHotness = (odds) => {
    const avg = (parseFloat(odds?.team1 || 2) + parseFloat(odds?.team2 || 2)) / 2;
    if (avg < 2.5) return 'hot';
    if (avg < 3.5) return 'warm';
    return 'cool';
  };

  if (loading) {
    return (
      <Card shadow="sm" padding="lg" radius="lg" withBorder>
        <Group position="center" style={{ padding: '60px 0' }}>
          <Loader size="xl" />
        </Group>
      </Card>
    );
  }

  return (
    <Stack spacing="lg" className="fade-in">
      {/* Header Section */}
      <Card shadow="md" padding="lg" radius="lg" withBorder>
        <Group position="apart">
          <div>
            <Title order={2} style={{ marginBottom: 8 }}>
              🔥 Live & Upcoming Matches
            </Title>
            <Text color="dimmed">
              {events.length} matches available • Updated in real-time
            </Text>
          </div>
          
          {/* Filter Buttons */}
          <Group spacing="sm">
            <button 
              className={`button button-sm ${filter === 'all' ? 'button-blue button-filled' : 'button-light'}`}
              onClick={() => setFilter('all')}
            >
              All Matches
            </button>
            <button 
              className={`button button-sm ${filter === 'today' ? 'button-blue button-filled' : 'button-light'}`}
              onClick={() => setFilter('today')}
            >
              Today
            </button>
            <button 
              className={`button button-sm ${filter === 'upcoming' ? 'button-blue button-filled' : 'button-light'}`}
              onClick={() => setFilter('upcoming')}
            >
              Upcoming
            </button>
          </Group>
        </Group>
      </Card>

      {/* Events Grid */}
      <Grid>
        {events.map((event, idx) => {
          const hotness = getHotness({ team1: event?.odds_team1, team2: event?.odds_team2 });
          
          return (
            <GridCol key={event?.id || idx} span={12} md={6} className="slide-in-up" style={{ animationDelay: `${idx * 0.05}s` }}>
              <Card 
                shadow="md" 
                padding="lg" 
                radius="lg" 
                withBorder
                style={{ 
                  height: '100%',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                {/* Hotness Indicator */}
                {hotness === 'hot' && (
                  <div style={{
                    position: 'absolute',
                    top: 12,
                    right: 12,
                    zIndex: 10
                  }}>
                    <Badge color="red" size="sm" style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
                      <IconFlame size={14} />
                      HOT
                    </Badge>
                  </div>
                )}

                <Stack spacing="md">
                  {/* Match Header */}
                  <Group position="apart">
                    <Badge 
                      color={event?.status === 'upcoming' ? 'blue' : 'green'} 
                      variant="filled"
                      size="md"
                    >
                      {event?.status?.toUpperCase() || 'UPCOMING'}
                    </Badge>
                    <Group spacing="xs">
                      <IconCalendar size={16} style={{ color: 'rgba(255, 255, 255, 0.6)' }} />
                      <Text size="sm" color="dimmed">
                        {event?.date ? new Date(event.date).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric' 
                        }) : 'TBD'}
                      </Text>
                    </Group>
                  </Group>

                  {/* Teams Display */}
                  <div style={{ 
                    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1))',
                    padding: '20px',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 255, 255, 0.05)'
                  }}>
                    <Group position="center" spacing="lg">
                      <div style={{ 
                        textAlign: 'center', 
                        flex: 1,
                        padding: '12px',
                        background: 'rgba(255, 255, 255, 0.03)',
                        borderRadius: '10px'
                      }}>
                        <Text size="xl" weight={700} style={{ fontSize: '1.5rem' }}>
                          {event?.team1 || 'Team 1'}
                        </Text>
                        <Text size="xs" color="dimmed" style={{ marginTop: 4 }}>
                          HOME
                        </Text>
                      </div>
                      
                      <div style={{
                        padding: '12px 20px',
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        borderRadius: '12px',
                        fontWeight: 700,
                        fontSize: '1.25rem',
                        boxShadow: '0 4px 16px rgba(99, 102, 241, 0.3)'
                      }}>
                        VS
                      </div>
                      
                      <div style={{ 
                        textAlign: 'center', 
                        flex: 1,
                        padding: '12px',
                        background: 'rgba(255, 255, 255, 0.03)',
                        borderRadius: '10px'
                      }}>
                        <Text size="xl" weight={700} style={{ fontSize: '1.5rem' }}>
                          {event?.team2 || 'Team 2'}
                        </Text>
                        <Text size="xs" color="dimmed" style={{ marginTop: 4 }}>
                          AWAY
                        </Text>
                      </div>
                    </Group>

                    <Group position="center" spacing="xs" style={{ marginTop: 16 }}>
                      <IconClock size={16} style={{ color: 'rgba(255, 255, 255, 0.6)' }} />
                      <Text size="sm" weight={600} color="dimmed">
                        {event?.date ? new Date(event.date).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        }) : 'TBD'}
                      </Text>
                    </Group>
                  </div>

                  {/* Betting Odds */}
                  <div>
                    <Group position="apart" style={{ marginBottom: 12 }}>
                      <Text size="sm" weight={600} style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 6 
                      }}>
                        <IconTrendingUp size={16} />
                        Live Odds
                      </Text>
                      <Badge color="purple" variant="light" size="sm">
                        AI Powered
                      </Badge>
                    </Group>
                    
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: '1fr 1fr 1fr', 
                      gap: '10px' 
                    }}>
                      <div style={{
                        textAlign: 'center',
                        padding: '14px',
                        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.15))',
                        borderRadius: '10px',
                        border: '1px solid rgba(16, 185, 129, 0.2)'
                      }}>
                        <Text size="xs" color="dimmed" style={{ marginBottom: 6 }}>
                          HOME WIN
                        </Text>
                        <Badge color="green" size="lg" style={{ 
                          fontSize: '1.1rem',
                          padding: '8px 16px'
                        }}>
                          {safeToFixed(event?.odds_team1)}
                        </Badge>
                      </div>
                      
                      <div style={{
                        textAlign: 'center',
                        padding: '14px',
                        background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.15))',
                        borderRadius: '10px',
                        border: '1px solid rgba(245, 158, 11, 0.2)'
                      }}>
                        <Text size="xs" color="dimmed" style={{ marginBottom: 6 }}>
                          DRAW
                        </Text>
                        <Badge color="yellow" size="lg" style={{ 
                          fontSize: '1.1rem',
                          padding: '8px 16px'
                        }}>
                          {safeToFixed(event?.odds_draw)}
                        </Badge>
                      </div>
                      
                      <div style={{
                        textAlign: 'center',
                        padding: '14px',
                        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(79, 70, 229, 0.15))',
                        borderRadius: '10px',
                        border: '1px solid rgba(99, 102, 241, 0.2)'
                      }}>
                        <Text size="xs" color="dimmed" style={{ marginBottom: 6 }}>
                          AWAY WIN
                        </Text>
                        <Badge color="blue" size="lg" style={{ 
                          fontSize: '1.1rem',
                          padding: '8px 16px'
                        }}>
                          {safeToFixed(event?.odds_team2)}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Action Button */}
                  <button 
                    className="button button-purple button-filled button-md"
                    style={{ width: '100%', marginTop: 8 }}
                    onClick={() => {/* Navigate to predictions */}}
                  >
                    <IconChartBar size={18} />
                    View AI Analysis
                  </button>
                </Stack>
              </Card>
            </GridCol>
          );
        })}
      </Grid>

      {/* Empty State */}
      {events.length === 0 && (
        <Card shadow="sm" padding="xl" radius="lg" withBorder>
          <Stack align="center" spacing="md" style={{ padding: '40px 0' }}>
            <IconTrophy size={64} style={{ color: 'rgba(255, 255, 255, 0.3)' }} />
            <Title order={3} style={{ textAlign: 'center' }}>
              No Events Available
            </Title>
            <Text align="center" color="dimmed" style={{ maxWidth: 400 }}>
              There are no matches scheduled at the moment. Check back soon for upcoming fixtures!
            </Text>
          </Stack>
        </Card>
      )}
    </Stack>
  );
}
