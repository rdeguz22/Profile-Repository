import api from './api';
import { Game, GameCreate, GameStats } from '../types';

export const gameAPI = {
  getAll: (params?: { season?: string; status?: string; team?: string }) => 
    api.get<Game[]>('/api/games', { params }),
  
  getById: (id: number) => 
    api.get<Game>(`/api/games/${id}`),
  
  create: (game: GameCreate) => 
    api.post<Game>('/api/games', game),
  
  update: (id: number, game: Partial<Game>) => 
    api.put<Game>(`/api/games/${id}`, game),
  
  delete: (id: number) => 
    api.delete(`/api/games/${id}`),
  
  addStats: (gameId: number, stats: GameStats) => 
    api.post(`/api/games/${gameId}/stats`, stats),
  
  getStats: (gameId: number) => 
    api.get(`/api/games/${gameId}/stats`),
};