import React, { useEffect, useState } from 'react';
import { gameAPI } from '../services/gameAPI';
import { Game } from '../types';

const GameList: React.FC = () => {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    fetchGames();
  }, [filterSeason, filterStatus]);

  const fetchGames = async () => {
    try {
      const params: any = {};
      if (filterSeason) params.season = filterSeason;
      if (filterStatus) params.status = filterStatus;
      
      const response = await gameAPI.getAll(params);
      setGames(response.data);
    } catch (error) {
      console.error('Error fetching games:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateScore = async (gameId: number) => {
    const homeScore = prompt('Enter home score:');
    const awayScore = prompt('Enter away score:');
    
    if (homeScore && awayScore) {
      try {
        await gameAPI.update(gameId, {
          home_score: parseInt(homeScore),
          away_score: parseInt(awayScore),
          status: 'completed',
        });
        fetchGames();
      } catch (error) {
        console.error('Error updating game:', error);
      }
    }
  };

  const handleDelete = async (gameId: number) => {
    if (window.confirm('Are you sure you want to delete this game?')) {
      try {
        await gameAPI.delete(gameId);
        fetchGames();
      } catch (error) {
        console.error('Error deleting game:', error);
      }
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading games...</div>;
  }

  const seasons = Array.from(new Set(games.map(g => g.season)));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Games ({games.length})</h2>
        
        <div className="flex gap-2">
          <select
            value={filterSeason}
            onChange={(e) => setFilterSeason(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="">All Seasons</option>
            {seasons.map(season => (
              <option key={season} value={season}>{season}</option>
            ))}
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="">All Status</option>
            <option value="scheduled">Scheduled</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {games.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No games found. Schedule your first game!
        </div>
      ) : (
        <div className="space-y-4">
          {games.map((game) => (
            <div
              key={game.id}
              className="p-4 border rounded-lg hover:border-blue-300 transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-4">
                    <h3 className="font-bold text-lg">
                      {game.away_team} @ {game.home_team}
                    </h3>
                    <span className={`px-2 py-1 text-sm rounded ${
                      game.status === 'completed' 
                        ? 'bg-green-100 text-green-800'
                        : game.status === 'in_progress'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {game.status}
                    </span>
                  </div>
                  <p className="text-gray-600 mt-1">
                    {new Date(game.game_date).toLocaleDateString()} • {game.season}
                  </p>
                  {game.status !== 'scheduled' && (
                    <p className="text-2xl font-bold mt-2">
                      {game.away_score} - {game.home_score}
                    </p>
                  )}
                </div>

                <div className="flex gap-2">
                  {game.status !== 'completed' && (
                    <button
                      onClick={() => handleUpdateScore(game.id)}
                      className="text-blue-600 hover:text-blue-800 px-3 py-1 rounded hover:bg-blue-50"
                    >
                      Update Score
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(game.id)}
                    className="text-red-600 hover:text-red-800 px-3 py-1 rounded hover:bg-red-50"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GameList;