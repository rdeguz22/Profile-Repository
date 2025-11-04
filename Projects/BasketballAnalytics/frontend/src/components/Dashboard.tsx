import React, { useEffect, useState } from 'react';
import { playerAPI } from '../services/playerAPI';
import { gameAPI } from '../services/gameAPI';
import { statsAPI } from '../services/statsAPI';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalPlayers: 0,
    totalGames: 0,
    recentGames: [] as any[],
  });
  const [topScorers, setTopScorers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [players, games, scorers] = await Promise.all([
        playerAPI.getAll(),
        gameAPI.getAll(),
        statsAPI.getTopScorers(5),
      ]);

      setStats({
        totalPlayers: players.data.length,
        totalGames: games.data.length,
        recentGames: games.data.slice(0, 5),
      });
      setTopScorers(scorers.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Total Players</h3>
          <p className="text-4xl font-bold text-blue-600">{stats.totalPlayers}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-gray-600 text-sm font-medium mb-2">Total Games</h3>
          <p className="text-4xl font-bold text-green-600">{stats.totalGames}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-gray-600 text-sm font-medium mb-2">This Season</h3>
          <p className="text-4xl font-bold text-purple-600">2024-25</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">🏆 Top 5 Scorers</h3>
          {topScorers.length === 0 ? (
            <p className="text-gray-500">No statistics available yet</p>
          ) : (
            <div className="space-y-2">
              {topScorers.map((scorer, index) => (
                <div key={scorer.player_id} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-gray-400">#{index + 1}</span>
                    <div>
                      <p className="font-semibold">{scorer.name}</p>
                      <p className="text-sm text-gray-600">{scorer.team}</p>
                    </div>
                  </div>
                  <p className="text-xl font-bold text-blue-600">{scorer.avg_points}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">📅 Recent Games</h3>
          {stats.recentGames.length === 0 ? (
            <p className="text-gray-500">No games scheduled yet</p>
          ) : (
            <div className="space-y-2">
              {stats.recentGames.map((game: any) => (
                <div key={game.id} className="p-2 hover:bg-gray-50 rounded">
                  <p className="font-semibold">
                    {game.away_team} @ {game.home_team}
                  </p>
                  <p className="text-sm text-gray-600">
                    {new Date(game.game_date).toLocaleDateString()} • {game.status}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;