import React, { useState } from 'react';
import { gameAPI } from '../services/gameAPI';
import { GameCreate } from '../types';

interface GameFormProps {
  onSuccess: () => void;
}

const GameForm: React.FC<GameFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = useState<GameCreate>({
    home_team: '',
    away_team: '',
    game_date: '',
    season: '2024-2025',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await gameAPI.create(formData);
      setFormData({
        home_team: '',
        away_team: '',
        game_date: '',
        season: '2024-2025',
      });
      onSuccess();
      alert('Game created successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create game');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Schedule New Game</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Home Team *</label>
          <input
            type="text"
            name="home_team"
            required
            value={formData.home_team}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Lakers"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Away Team *</label>
          <input
            type="text"
            name="away_team"
            required
            value={formData.away_team}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Warriors"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Game Date *</label>
          <input
            type="date"
            name="game_date"
            required
            value={formData.game_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Season *</label>
          <input
            type="text"
            name="season"
            required
            value={formData.season}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="2024-2025"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition disabled:bg-gray-400"
        >
          {loading ? 'Creating...' : '📅 Schedule Game'}
        </button>
      </form>
    </div>
  );
};

export default GameForm;