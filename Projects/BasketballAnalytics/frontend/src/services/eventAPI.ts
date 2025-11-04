import api from './api';
import { GameEvent } from '../types';

export const eventAPI = {
  create: (gameId: number, event: Omit<GameEvent, 'id' | 'timestamp'>) => 
    api.post(`/api/games/${gameId}/events`, event),
  
  getAll: (gameId: number) => 
    api.get<GameEvent[]>(`/api/games/${gameId}/events`),
};