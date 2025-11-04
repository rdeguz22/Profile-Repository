import api from './api';
import { Player, PlayerCreate, PlayerStats } from '../types';

export const playerAPI = {
  getAll: (params?: { team?: string; position?: string }) => 
    api.get<Player[]>('/api/players', { params }),
  
  getById: (id: number) => 
    api.get<Player>(`/api/players/${id}`),
  
  create: (player: PlayerCreate) => 
    api.post<Player>('/api/players', player),
  
  update: (id: number, player: Partial<PlayerCreate>) => 
    api.put<Player>(`/api/players/${id}`, player),
  
  delete: (id: number) => 
    api.delete(`/api/players/${id}`),
  
  getStats: (id: number, season?: string) => 
    api.get<PlayerStats>(`/api/players/${id}/stats`, { params: { season } }),
  
  findSimilar: (id: number, topK: number = 5) => 
    api.get(`/api/players/${id}/similar`, { params: { top_k: topK } }),
};