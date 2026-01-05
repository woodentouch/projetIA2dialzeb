import React, { useState } from 'react';
import { IconTrophy, IconChartBar, IconListCheck, IconCash } from '@tabler/icons-react';
import EventsList from './components/EventsList';
import BettingDashboard from './components/BettingDashboard';
import MyBets from './components/MyBets';
import PredictionDashboard from './components/PredictionDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './styles/modern.css';

function App() {
  const [activeTab, setActiveTab] = useState('events');

  return (
    <div className="app-container">
      <div className="app-content">
        {/* Modern Header */}
        <div className="app-header">
          <div>
            <h1 className="app-title">
              ⚽ Football Betting AI
            </h1>
            <p className="app-subtitle">
              Professional Opta-Level Predictions & Smart Betting Platform
            </p>
          </div>
          <div className="app-header-icon">
            <IconTrophy size={32} color="white" />
          </div>
        </div>

        {/* Modern Tab Navigation */}
        <div className="tabs-container">
          <div className="tabs-list">
            <button
              className={`tab-button ${activeTab === 'events' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('events')}
            >
              <IconListCheck size={18} />
              <span>Live Events</span>
            </button>
            <button
              className={`tab-button ${activeTab === 'predictions' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('predictions')}
            >
              <IconChartBar size={18} />
              <span>AI Analytics</span>
            </button>
            <button
              className={`tab-button ${activeTab === 'betting' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('betting')}
            >
              <IconCash size={18} />
              <span>Place Bets</span>
            </button>
            <button
              className={`tab-button ${activeTab === 'mybets' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('mybets')}
            >
              <IconTrophy size={18} />
              <span>My Portfolio</span>
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'events' && <EventsList />}
            {activeTab === 'predictions' && (
              <ErrorBoundary>
                <PredictionDashboard />
              </ErrorBoundary>
            )}
            {activeTab === 'betting' && <BettingDashboard />}
            {activeTab === 'mybets' && <MyBets />}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
