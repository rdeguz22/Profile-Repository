import React, { useState } from 'react';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import PlayerForm from './components/PlayerForm';
import PlayerList from './components/PlayerList';
import GameForm from './components/GameForm';
import GameList from './components/GameList';
import LiveGameFeed from './components/LiveGameFeed';
import Leaderboard from './components/Leaderboard';
import './App.css';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="container mx-auto px-4 py-8">
        {activeTab === 'dashboard' && (
          <Dashboard key={refreshKey} />
        )}

        {activeTab === 'players' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <PlayerForm onSuccess={handleRefresh} />
            </div>
            <div className="lg:col-span-2">
              <PlayerList key={refreshKey} />
            </div>
          </div>
        )}

        {activeTab === 'games' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <GameForm onSuccess={handleRefresh} />
            </div>
            <div className="lg:col-span-2">
              <GameList key={refreshKey} />
            </div>
          </div>
        )}

        {activeTab === 'live' && (
          <LiveGameFeed key={refreshKey} />
        )}

        {activeTab === 'stats' && (
          <Leaderboard key={refreshKey} />
        )}
      </main>
    </div>
  );
};

export default App;