import React, { useState, useEffect } from 'react'
import { Button, Card, Text, Group, Loader, Space, Badge, Select } from '@mantine/core'
import axios from 'axios'

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from 'recharts'

export default function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [matches, setMatches] = useState([])
  const [teams, setTeams] = useState([])
  const [inferenceLoading, setInferenceLoading] = useState(false)
  const [inferenceResult, setInferenceResult] = useState(null)
  const [selectedTeam, setSelectedTeam] = useState(null)

  useEffect(() => {
    if (inferenceResult && inferenceResult.teams && inferenceResult.teams.length > 0) {
      setSelectedTeam(inferenceResult.teams[0])
    }
  }, [inferenceResult])

  const [inferenceMethod, setInferenceMethod] = useState('advi')
  const [inferenceDraws, setInferenceDraws] = useState(300)
  const [inferenceTune, setInferenceTune] = useState(300)

  function getHistogramData(samples, bins = 20) {
    if (!samples || samples.length === 0) return []
    const min = Math.min(...samples)
    const max = Math.max(...samples)
    const width = (max - min) / bins || 1
    const counts = new Array(bins).fill(0)
    for (const s of samples) {
      const idx = Math.min(bins - 1, Math.floor((s - min) / width))
      counts[idx]++
    }
    return counts.map((c, i) => ({ bin: (min + i * width).toFixed(2), count: c }))
  }

  function flattenDiagnostics(obj) {
    const out = []
    function rec(prefix, o) {
      if (typeof o === 'number') {
        out.push({ name: prefix, value: o })
        return
      }
      if (Array.isArray(o)) return
      if (o && typeof o === 'object') {
        for (const k of Object.keys(o)) rec(prefix ? `${prefix}.${k}` : k, o[k])
      }
    }
    rec('', obj)
    return out
  }

  function renderDiagnostics(diag) {
    const rhat = diag.rhat || {}
    const ess = diag.ess || {}
    const flatRhat = flattenDiagnostics(rhat)
    const flatEss = flattenDiagnostics(ess)
    // merge by name
    const map = {}
    for (const e of flatRhat) map[e.name] = { name: e.name, rhat: e.value }
    for (const e of flatEss) map[e.name] = { ...(map[e.name] || { name: e.name }), ess: e.value }
    const arr = Object.values(map).sort((a,b)=> (b.rhat||0)-(a.rhat||0)).slice(0,40)
    return (
      <div>
        {arr.map((a, idx) => (
          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 6px' }}>
            <Text size="sm">{a.name}</Text>
            <Text size="sm" color={a.rhat && a.rhat > 1.01 ? 'red' : 'teal'}>
              R̂: {a.rhat ? a.rhat.toFixed(3) : '—'} · ESS: {a.ess ? Math.round(a.ess) : '—'}
            </Text>
          </div>
        ))}
      </div>
    )
  }

  useEffect(() => {
    fetchMatches()
  }, [])

  const BACKEND = 'http://localhost:8000'

  async function fetchMatches() {
    try {
      const resp = await axios.get(`${BACKEND}/api/data/matches`)
      setMatches(resp.data.matches || [])
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchTeams() {
    try {
      const resp = await axios.get(`${BACKEND}/api/db/teams`)
      setTeams(resp.data.teams || [])
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchMatchesForTeam(name) {
    try {
      const resp = await axios.get(`${BACKEND}/api/db/matches`, { params: { team: name, limit: 200 } })
      setMatches(resp.data.matches || [])
    } catch (e) {
      console.error(e)
    }
  }

  async function rescrape() {
    setLoading(true)
    try {
      const resp = await axios.post(`${BACKEND}/api/scrape`)
      const jobId = resp.data.job_id
      // poll job status
      let status = 'queued'
      while (status !== 'finished' && status !== 'failed') {
        await new Promise((r) => setTimeout(r, 1500))
        const j = await axios.get(`${BACKEND}/api/jobs/${jobId}`)
        status = j.data.status
      }
      await fetchMatches()
      await fetchTeams()
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  async function runInference() {
    setInferenceLoading(true)
    setInferenceResult(null)
    try {
      const resp = await axios.post(`${BACKEND}/api/infer`, {}, { params: { method: inferenceMethod, draws: inferenceDraws, tune: inferenceTune } })
      const jobId = resp.data.job_id
      let status = 'queued'
      while (status !== 'finished' && status !== 'failed') {
        await new Promise((r) => setTimeout(r, 2000))
        const j = await axios.get(`${BACKEND}/api/jobs/${jobId}`)
        status = j.data.status
      }

      // fetch results
      const res = await axios.get(`${BACKEND}/api/infer/results/${jobId}`)
      setInferenceResult(res.data)
      // If diagnostics exist, expand selectedTeam to first team
      if (res.data.teams && res.data.teams.length > 0) setSelectedTeam(res.data.teams[0])
    } catch (e) {
      console.error(e)
    } finally {
      setInferenceLoading(false)
    }
  }

  return (
    <div>
      <Group position="apart">
        <Text weight={700}>Matches ({matches.length})</Text>
        <Group>
          <Button onClick={rescrape} color="blue" disabled={loading}>
            {loading ? <Loader size="xs" /> : 'Rescrape'}
          </Button>
          <Select
            value={inferenceMethod}
            onChange={(v) => setInferenceMethod(v)}
            data={[{ value: 'advi', label: 'ADVI (fast)' }, { value: 'mcmc', label: 'MCMC (slower, more accurate)' }]}
            size="xs"
            style={{ width: 200 }}
          />
          {inferenceMethod === 'mcmc' && (
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input type="number" min={50} value={inferenceDraws} onChange={(e)=>setInferenceDraws(Number(e.target.value))} style={{ width: 80 }} />
              <input type="number" min={50} value={inferenceTune} onChange={(e)=>setInferenceTune(Number(e.target.value))} style={{ width: 80 }} />
            </div>
          )}
          <Button color="green" onClick={runInference} disabled={inferenceLoading}>
            {inferenceLoading ? <Loader size="xs" /> : 'Run Inference'}
          </Button>
        </Group>
      </Group>

      <Space h="sm" />

      <Group position="apart" align="center">
        <Text weight={600}>Teams ({teams.length})</Text>
        <Button variant="outline" size="xs" onClick={fetchTeams}>Load teams</Button>
      </Group>

      <Space h="sm" />

      <Group spacing="xs">
        {teams.slice(0, 40).map((t, idx) => (
          <Badge key={idx} variant="light" onClick={() => fetchMatchesForTeam(t.name)} style={{ cursor: 'pointer' }}>{t.name}</Badge>
        ))}
      </Group>

      <Space h="sm" />

      {matches.slice(0, 10).map((m, idx) => (
        <Card key={idx} shadow="sm" padding="sm" style={{ marginTop: 8 }}>
          <Group position="apart">
            <Text>{m.date}</Text>
            <Text>{m.team1} {m.score1} — {m.score2} {m.team2}</Text>
          </Group>
        </Card>
      ))}

      {matches.length === 0 && <Text color="dimmed">Aucune donnée disponible. Cliquez sur Rescrape pour lancer une collecte.</Text>}

      <Space h="md" />
      <Card shadow="sm" padding="sm">
        <Text weight={600}>Inference Result</Text>
        {inferenceLoading && <Text color="dimmed">Running inference...</Text>}
        {inferenceResult && (
          <div>
            <Text size="sm">Matches used: {inferenceResult.n_matches} — Teams: {inferenceResult.n_teams}</Text>
            <Space h="sm" />
            <Text weight={600}>Top teams by attack mean</Text>
            <div>
              {Object.entries(inferenceResult.attack_means || {}).sort((a,b)=>b[1]-a[1]).slice(0,10).map(([name,val],idx)=> (
                <Text key={idx}>{name}: {val.toFixed(3)}</Text>
              ))}
            </div>

            <Space h="md" />

            {/* Trace plot for mu */}
            {inferenceResult.posteriors && inferenceResult.posteriors.mu && (
              <div style={{ height: 180 }}>
                <Text weight={600}>Trace: mu</Text>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={inferenceResult.posteriors.mu.map((v, i) => ({ x: i, y: v }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="x" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="y" stroke="#8884d8" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            <Space h="md" />

            {/* Diagnostics: R_hat / ESS */}
            {inferenceResult.diagnostics && (
              <div>
                <Text weight={600}>Diagnostics (R_hat & ESS)</Text>
                <Space h="sm" />
                <div style={{ maxHeight: 140, overflow: 'auto', padding: 8, background: '#f8f9fa', borderRadius: 6 }}>
                  {renderDiagnostics(inferenceResult.diagnostics)}
                </div>
              </div>
            )}

            <Space h="md" />

            {/* Histogram for selected team's attack posterior */}
            {inferenceResult.posteriors && inferenceResult.posteriors.attack && (
              <div>
                <Text weight={600}>Team attack posterior</Text>
                <Space h="sm" />
                <Select
                  data={inferenceResult.teams || []}
                  placeholder="Select a team"
                  onChange={(val) => setSelectedTeam(val)}
                />
                <Space h="sm" />
                {selectedTeam && inferenceResult.posteriors.attack[selectedTeam] && (
                  <div style={{ height: 220 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getHistogramData(inferenceResult.posteriors.attack[selectedTeam], 20)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="bin" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}

          </div>
        )}
        {!inferenceResult && !inferenceLoading && <Text color="dimmed">No inference result yet. Click Run Inference.</Text>}
      </Card>
    </div>
  )
}
