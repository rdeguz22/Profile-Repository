import React, { useEffect, useState } from 'react';
import { statsAPI } from '../services/statsAPI';
import { TopScorer } from '../types';

const Leaderboard: React.FC = () => {
  const [topScorers, setTopScorers] = useState<TopScorer[]>([]);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    fetchTopScorers();
  }, [limit]);

  const fetchTopScorers = async () => {
    try {
      const response = await statsAPI.getTopScorers(limit);
      setTopScorers(response.data);
    } catch (error) {
      console.error('Error fetching top scorers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading leaderboard...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">🏆 Top Scorers</h2>
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="px-3 py-2 border rounded-md"
        >
          <option value={5}>Top 5</option>
          <option value={10}>Top 10</option>
          <option value={20}>Top 20</option>
        </select>
      </div>

      {topScorers.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No statistics available yet
        </div>
      ) : (
        <div className="space-y-3">
          {topScorers.map((scorer, index) => (
            <div
              key={scorer.player_id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition"
            >
              <div className="flex items-center gap-4">
                <div className={`text-2xl font-bold w-8 ${
                  index === 0 ? 'text-yellow-500' :
                  index === 1 ? 'text-gray-400' :
                  index === 2 ? 'text-orange-600' :
                  'text-gray-600'
                }`}>
                  #{index + 1}
                </div>
                <div>
                  <h3 className="font-bold">{scorer.name}</h3>
                  <p className="text-sm text-gray-600">
                    {scorer.team} • {scorer.games_played} games
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-blue-600">
                  {scorer.avg_points}
                </p>
                <p className="text-sm text-gray-600">PPG</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Leaderboard;