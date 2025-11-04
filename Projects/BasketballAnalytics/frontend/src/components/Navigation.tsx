import React from 'react';

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
    { id: 'players', label: '👥 Players', icon: '👥' },
    { id: 'games', label: '🏟️ Games', icon: '🏟️' },
    { id: 'live', label: '🔴 Live Feed', icon: '🔴' },
    { id: 'stats', label: '📈 Statistics', icon: '📈' },
  ];

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          <h1 className="text-2xl font-bold">🏀 Basketball Platform</h1>
          <div className="flex space-x-4">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`px-4 py-2 rounded transition ${
                  activeTab === tab.id
                    ? 'bg-blue-800'
                    : 'hover:bg-blue-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;