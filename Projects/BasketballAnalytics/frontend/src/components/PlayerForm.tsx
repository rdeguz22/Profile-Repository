import React, { useState } from 'react';
import { playerAPI } from '../services/playerAPI';
import { PlayerCreate } from '../types';

interface PlayerFormProps {
  onSuccess: () => void;
}

const PlayerForm: React.FC<PlayerFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = useState<PlayerCreate>({
    name: '',
    team: '',
    position: 'PG',
    height: 75,
    weight: 200,
    jersey_number: 0,
    birth_date: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await playerAPI.create(formData);
      setFormData({
        name: '',
        team: '',
        position: 'PG',
        height: 75,
        weight: 200,
        jersey_number: 0,
        birth_date: '',
      });
      onSuccess();
      alert('Player created successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create player');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'height' || name === 'weight' || name === 'jersey_number' 
        ? Number(value) 
        : value,
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Add New Player</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Name *</label>
          <input
            type="text"
            name="name"
            required
            value={formData.name}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="LeBron James"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Team *</label>
          <input
            type="text"
            name="team"
            required
            value={formData.team}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Lakers"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Position *</label>
          <select
            name="position"
            value={formData.position}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="PG">Point Guard (PG)</option>
            <option value="SG">Shooting Guard (SG)</option>
            <option value="SF">Small Forward (SF)</option>
            <option value="PF">Power Forward (PF)</option>
            <option value="C">Center (C)</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Height (inches) *</label>
            <input
              type="number"
              name="height"
              required
              min="60"
              max="90"
              value={formData.height}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Weight (lbs) *</label>
            <input
              type="number"
              name="weight"
              required
              min="150"
              max="350"
              value={formData.weight}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Jersey Number *</label>
          <input
            type="number"
            name="jersey_number"
            required
            min="0"
            max="99"
            value={formData.jersey_number}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Birth Date *</label>
          <input
            type="date"
            name="birth_date"
            required
            value={formData.birth_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition disabled:bg-gray-400"
        >
          {loading ? 'Creating...' : '➕ Add Player'}
        </button>
      </form>
    </div>
  );
};

export default PlayerForm;