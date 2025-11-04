import React, { useEffect, useState } from 'react';
import { playerAPI } from '../services/playerAPI';
import { Player, PlayerStats } from '../types';
import PlayerCard from './PlayerCard';

const PlayerList: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [playerStats, setPlayerStats] = useState<PlayerStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterTeam, setFilterTeam] = useState('');
  const [filterPosition, setFilterPosition] = useState('');

  useEffect(() => {
    fetchPlayers();
  }, [filterTeam, filterPosition]);

  const fetchPlayers = async () => {
    try {
      const params: any = {};
      if (filterTeam) params.team = filterTeam;
      if (filterPosition) params.position = filterPosition;
      
      const response = await playerAPI.getAll(params);
      setPlayers(response.data);
    } catch (error) {
      console.error('Error fetching players:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayerClick = async (playerId: number) => {
    setSelectedPlayer(playerId);
    try {
      const response = await playerAPI.getStats(playerId);
      setPlayerStats(response.data);
    } catch (error) {
      console.error('Error fetching player stats:', error);
    }
  };

  const handleDelete = async (playerId: number) => {
    if (window.confirm('Are you sure you want to delete this player?')) {
      try {
        await playerAPI.delete(playerId);
        fetchPlayers();
        if (selectedPlayer === playerId) {
          setSelectedPlayer(null);
          setPlayerStats(null);
        }
      } catch (error) {
        console.error('Error deleting player:', error);
      }
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading players...</div>;
  }

  // Get unique teams and positions for filters
  const teams = Array.from(new Set(players.map(p => p.team)));
  const positions = ['PG', 'SG', 'SF', 'PF', 'C'];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Players ({players.length})</h2>
        
        <div className="flex gap-2">
          <select
            value={filterTeam}
            onChange={(e) => setFilterTeam(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="">All Teams</option>
            {teams.map(team => (
              <option key={team} value={team}>{team}</option>
            ))}
          </select>

          <select
            value={filterPosition}
            onChange={(e) => setFilterPosition(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="">All Positions</option>
            {positions.map(pos => (
              <option key={pos} value={pos}>{pos}</option>
            ))}
          </select>
        </div>
      </div>

      {players.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No players found. Add your first player!
        </div>
      ) : (
        <div className="space-y-4">
          {players.map((player) => (
            <PlayerCard
              key={player.id}
              player={player}
              isSelected={selectedPlayer === player.id}
              stats={selectedPlayer === player.id ? playerStats : null}
              onClick={() => handlePlayerClick(player.id)}
              onDelete={() => handleDelete(player.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default PlayerList;