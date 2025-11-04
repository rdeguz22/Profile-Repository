import api from './api';
import { TopScorer, TeamStats } from '../types';

export const statsAPI = {
  getTopScorers: (limit: number = 10, season?: string) => 
    api.get<TopScorer[]>('/api/stats/top-scorers', { params: { limit, season } }),
  
  getTeamStats: (team: string, season?: string) => 
    api.get<TeamStats>('/api/stats/team', { params: { team, season } }),
  
  getLeaderboard: (stat: string, limit: number = 10, season?: string) => 
    api.get('/api/stats/leaderboard', { params: { stat, limit, season } }),
};