import { useState, useEffect } from 'react';
import { Card, Title, Text, Badge, Group, Stack, Table, Loader, Alert, Button } from './CustomComponents';
import { IconAlertCircle, IconRefresh } from '@tabler/icons-react';
import axios from 'axios';
import { safeNumber, safeDate, safeMultiply, safeGet } from '../utils';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function MyBets() {
  const [bets, setBets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadBets();
  }, []);

  const loadBets = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/api/my-bets?user_id=1`);
      setBets(safeGet(response, 'data.bets', []));
    } catch (err) {
      console.error('Failed to load bets:', err);
      setError('Failed to load your bets. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const calculateTotal = (key) => {
    return bets.reduce((sum, bet) => {
      const value = Number(safeGet(bet, key, 0));
      return sum + (Number.isFinite(value) ? value : 0);
    }, 0);
  };

  const totalStaked = calculateTotal('amount');
  const totalPotential = bets.reduce((sum, bet) => {
    const amount = Number(safeGet(bet, 'amount', 0));
    const odds = Number(safeGet(bet, 'odds', 0));
    if (Number.isFinite(amount) && Number.isFinite(odds)) {
      return sum + (amount * odds);
    }
    return sum;
  }, 0);

  const getStatusColor = (status) => {
    const colors = {
      pending: 'blue',
      won: 'green',
      lost: 'red',
      cancelled: 'gray'
    };
    return colors[String(status).toLowerCase()] || 'gray';
  };

  if (loading) {
    return (
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="center" py="xl">
          <Loader size="xl" />
        </Group>
      </Card>
    );
  }

  return (
    <Stack gap="md">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Title order={2}>My Betting History</Title>
          <Button
            variant="light"
            leftSection={<IconRefresh size={16} />}
            onClick={loadBets}
            disabled={loading}
          >
            Refresh
          </Button>
        </Group>
        <Group justify="space-between">
          <div>
            <Text size="sm" c="dimmed">Total Staked</Text>
            <Text size="xl" fw={700}>€{safeNumber(totalStaked)}</Text>
          </div>
          <div>
            <Text size="sm" c="dimmed">Potential Winnings</Text>
            <Text size="xl" fw={700} c="green">€{safeNumber(totalPotential)}</Text>
          </div>
          <div>
            <Text size="sm" c="dimmed">Total Bets</Text>
            <Text size="xl" fw={700}>{bets.length}</Text>
          </div>
        </Group>
      </Card>

      {error && (
        <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
          {error}
        </Alert>
      )}

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        {bets.length > 0 ? (
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>ID</Table.Th>
                <Table.Th>Event</Table.Th>
                <Table.Th>Type</Table.Th>
                <Table.Th>Amount</Table.Th>
                <Table.Th>Odds</Table.Th>
                <Table.Th>Potential Win</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Date</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {bets.map((bet) => {
                const amount = Number(safeGet(bet, 'amount', 0));
                const odds = Number(safeGet(bet, 'odds', 0));
                return (
                  <Table.Tr key={safeGet(bet, 'id', Math.random())}>
                    <Table.Td>#{safeGet(bet, 'id', 'N/A')}</Table.Td>
                    <Table.Td>Event #{safeGet(bet, 'event_id', 'N/A')}</Table.Td>
                    <Table.Td>
                      <Badge variant="outline">{safeGet(bet, 'bet_type', 'unknown')}</Badge>
                    </Table.Td>
                    <Table.Td>€{safeNumber(amount)}</Table.Td>
                    <Table.Td>{safeNumber(odds)}</Table.Td>
                    <Table.Td>€{safeMultiply(amount, odds)}</Table.Td>
                    <Table.Td>
                      <Badge color={getStatusColor(safeGet(bet, 'status'))}>
                        {safeGet(bet, 'status', 'unknown')}
                      </Badge>
                    </Table.Td>
                    <Table.Td>{safeDate(safeGet(bet, 'created_at'))}</Table.Td>
                  </Table.Tr>
                );
              })}
            </Table.Tbody>
          </Table>
        ) : (
          <Text ta="center" c="dimmed" py="xl">
            No bets placed yet. Start betting now!
          </Text>
        )}
      </Card>
    </Stack>
  );
}
