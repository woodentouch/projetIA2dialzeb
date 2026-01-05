import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Title, Text, Badge, Group, Stack, Table, Loader } from './CustomComponents';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const safeToFixed = (value, decimals = 2) => {
  if (value === undefined || value === null || isNaN(value)) return 'N/A';
  const num = Number(value);
  if (isNaN(num) || !isFinite(num)) return 'N/A';
  return num.toFixed(decimals);
};

export default function MyBets() {
  const [bets, setBets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBets();
  }, []);

  const loadBets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/my-bets?user_id=1`);
      setBets(response.data.bets || []);
    } catch (err) {
      console.error('Failed to load bets:', err);
    } finally {
      setLoading(false);
    }
  };

  const totalStaked = bets.reduce((sum, bet) => sum + (Number(bet?.amount) || 0), 0);
  const totalPotential = bets.reduce((sum, bet) => {
    const amount = Number(bet?.amount) || 0;
    const odds = Number(bet?.odds) || 0;
    return sum + (amount * odds);
  }, 0);

  const getStatusColor = (status) => {
    const colors = {
      pending: 'blue',
      won: 'green',
      lost: 'red',
      cancelled: 'gray'
    };
    return colors[status] || 'gray';
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
        <Title order={2} mb="md">My Betting History</Title>
        <Group position="apart">
          <div>
            <Text size="sm" color="dimmed">Total Staked</Text>
            <Text size="xl" weight={700}>€{safeToFixed(totalStaked)}</Text>
          </div>
          <div>
            <Text size="sm" color="dimmed">Potential Winnings</Text>
            <Text size="xl" weight={700} color="green">€{safeToFixed(totalPotential)}</Text>
          </div>
          <div>
            <Text size="sm" color="dimmed">Total Bets</Text>
            <Text size="xl" weight={700}>{bets.length}</Text>
          </div>
        </Group>
      </Card>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        {bets.length > 0 ? (
          <Table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Event</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Odds</th>
                <th>Potential Win</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {bets.map((bet) => {
                const amount = Number(bet?.amount) || 0;
                const odds = Number(bet?.odds) || 0;
                return (
                  <tr key={bet?.id || Math.random()}>
                    <td>#{bet?.id || 'N/A'}</td>
                    <td>Event #{bet?.event_id || 'N/A'}</td>
                    <td>
                      <Badge variant="outline">{bet?.bet_type || 'unknown'}</Badge>
                    </td>
                    <td>€{safeToFixed(amount)}</td>
                    <td>{safeToFixed(odds)}</td>
                    <td>€{safeToFixed(amount * odds)}</td>
                    <td>
                      <Badge color={getStatusColor(bet?.status)}>
                        {bet?.status || 'unknown'}
                      </Badge>
                    </td>
                    <td>{bet?.created_at ? new Date(bet.created_at).toLocaleDateString() : 'N/A'}</td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        ) : (
          <Text align="center" color="dimmed" py="xl">
            No bets placed yet. Start betting now!
          </Text>
        )}
      </Card>
    </Stack>
  );
}
