export interface Player {
    id: number;
    name: string;
    team: string;
    position: string;
    height: number;
    weight: number;
    jersey_number: number;
    birth_date: string;
  }
  
  export interface PlayerCreate {
    name: string;
    team: string;
    position: string;
    height: number;
    weight: number;
    jersey_number: number;
    birth_date: string;
  }
  
  export interface PlayerStats {
    total_games: number;
    totals: {
      points: number;
      assists: number;
      rebounds: number;
      steals: number;
      blocks: number;
      turnovers: number;
      field_goals_made: number;
      field_goals_attempted: number;
      three_pointers_made: number;
      three_pointers_attempted: number;
      minutes_played: number;
    };
    averages: {
      points: number;
      assists: number;
      rebounds: number;
      steals: number;
      blocks: number;
      turnovers: number;
      field_goal_pct: number;
      three_point_pct: number;
      minutes: number;
    };
  }
  
  export interface Game {
    id: number;
    home_team: string;
    away_team: string;
    home_score: number;
    away_score: number;
    game_date: string;
    season: string;
    status: string;
  }
  
  export interface GameCreate {
    home_team: string;
    away_team: string;
    game_date: string;
    season: string;
  }
  
  export interface GameStats {
    player_id: number;
    game_id: number;
    points: number;
    assists: number;
    rebounds: number;
    steals: number;
    blocks: number;
    turnovers: number;
    fouls: number;
    field_goals_made: number;
    field_goals_attempted: number;
    three_pointers_made: number;
    three_pointers_attempted: number;
    free_throws_made: number;
    free_throws_attempted: number;
    minutes_played: number;
  }
  
  export interface GameEvent {
    id: string;
    game_id: number;
    event_type: string;
    player_id: number;
    player_name: string;
    team: string;
    quarter: number;
    time_remaining: string;
    description: string;
    timestamp: string;
  }
  
  export interface TopScorer {
    player_id: number;
    name: string;
    team: string;
    avg_points: number;
    games_played: number;
  }
  
  export interface TeamStats {
    team: string;
    season: string;
    avg_points: number;
    avg_assists: number;
    avg_rebounds: number;
    total_games: number;
  }