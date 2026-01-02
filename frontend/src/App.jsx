import React from 'react'
import { Container, Title, Space } from '@mantine/core'
import Dashboard from './components/Dashboard'

export default function App() {
  return (
    <Container size="lg" padding="md">
      <Title order={2} align="center">Bayesian Sports Analytics (Football)</Title>
      <Space h="md" />
      <Dashboard />
    </Container>
  )
}
