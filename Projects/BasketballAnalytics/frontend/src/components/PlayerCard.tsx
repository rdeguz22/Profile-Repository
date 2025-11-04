import React from 'react';
import { Player, PlayerStats } from '../types';

interface PlayerCardProps {
  player: Player;
  isSelected: boolean;
  stats: PlayerStats | null;
  onClick: () => void;
  onDelete: () => void;
}

const PlayerCard: React.FC<PlayerCardProps> = ({ 
  player, 
  isSelected, 
  stats, 
  onClick, 
  onDelete 
}) => {
  return (
    <div
      onClick={onClick}
      className={`p-4 border rounded-lg cursor-pointer transition ${
        isSelected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-blue-300'
      }`}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-bold text-lg">{player.name}</h3>
          <p className="text-gray-600">
            {player.team} • #{player.jersey_number} • {player.position}
          </p>
          <p className="text-sm text-gray-500">
            {Math.floor(player.height / 12)}'{player.height % 12}" • {player.weight} lbs
          </p>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="text-red-600 hover:text-red-800 px-3 py-1 rounded hover:bg-red-50"
        >
          Delete
        </button>
      </div>

      {isSelected && stats && stats.total_games > 0 && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="font-semibold mb-2">Season Averages ({stats.total_games} games)</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">
                {stats.averages.points}
              </p>
              <p className="text-sm text-gray-600">PPG</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">
                {stats.averages.assists}
              </p>
              <p className="text-sm text-gray-600">APG</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">
                {stats.averages.rebounds}
              </p>
              <p className="text-sm text-gray-600">RPG</p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 text-center mt-2">
            <div>
              <p className="text-sm">FG: {stats.averages.field_goal_pct}%</p>
            </div>
            <div>
              <p className="text-sm">3PT: {stats.averages.three_point_pct}%</p>
            </div>
            <div>
              <p className="text-sm">{stats.averages.minutes} MIN</p>
            </div>
          </div>
        </div>
      )}

      {isSelected && stats && stats.total_games === 0 && (
        <div className="mt-4 pt-4 border-t text-center text-gray-500">
          No statistics available yet
        </div>
      )}
    </div>
  );
};

export default PlayerCard;