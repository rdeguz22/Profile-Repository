import React, { useEffect, useState } from 'react';
import { gameAPI } from '../services/gameAPI';
import { eventAPI } from '../services/eventAPI';
import { Game, GameEvent } from '../types';

const LiveGameFeed: React.FC = () => {
  const [games, setGames] = useState<Game[]>([]);
  const [selectedGame, setSelectedGame] = useState<number | null>(null);
  const [events, setEvents] = useState<GameEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGames();
  }, []);

  useEffect(() => {
    if (selectedGame) {
      fetchEvents();
      const interval = setInterval(fetchEvents, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedGame]);

  const fetchGames = async () => {
    try {
      const response = await gameAPI.getAll();
      setGames(response.data);
    } catch (error) {
      console.error('Error fetching games:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEvents = async () => {
    if (!selectedGame) return;
    
    try {
      const response = await eventAPI.getAll(selectedGame);
      setEvents(response.data.reverse());
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const addEvent = async () => {
    if (!selectedGame) return;

    const playerName = prompt('Player name:');
    const description = prompt('Event description:');
    
    if (playerName && description) {
      try {
        await eventAPI.create(selectedGame, {
          game_id: selectedGame,
          event_type: 'play',
          player_id: 1,
          player_name: playerName,
          team: 'Team',
          quarter: 1,
          time_remaining: '10:00',
          description: description,
        });
        fetchEvents();
      } catch (error) {
        console.error('Error adding event:', error);
      }
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading games...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">Select Game</h2>
        <div className="space-y-2">
          {games.map((game) => (
            <button
              key={game.id}
              onClick={() => setSelectedGame(game.id)}
              className={`w-full text-left p-4 border rounded-lg transition ${
                selectedGame === game.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-bold">
                    {game.away_team} @ {game.home_team}
                  </p>
                  <p className="text-sm text-gray-600">
                    {new Date(game.game_date).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-2xl font-bold">
                  {game.away_score} - {game.home_score}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {selectedGame && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">🔴 Live Game Feed</h2>
            <button
              onClick={addEvent}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Add Event
            </button>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {events.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No events yet. Add the first event!
              </div>
            ) : (
              events.map((event) => (
                <div
                  key={event.id}
                  className="p-3 border-l-4 border-blue-500 bg-gray-50 rounded animate-fade-in"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold">{event.player_name}</p>
                      <p className="text-sm text-gray-600">{event.description}</p>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <p>Q{event.quarter}</p>
                      <p>{event.time_remaining}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveGameFeed;