\c basketball_db;

DROP TABLE IF EXISTS player_stats CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS players CASCADE;

-- Players Table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    team VARCHAR(100) NOT NULL,
    position VARCHAR(10) NOT NULL,
    height FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    jersey_number INTEGER NOT NULL,
    birth_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Games Table
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    game_date DATE NOT NULL,
    season VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT status_check CHECK (status IN ('scheduled', 'in_progress', 'completed'))
);

-- Player Stats Table
CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    
    points INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    rebounds INTEGER DEFAULT 0,
    steals INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    turnovers INTEGER DEFAULT 0,
    fouls INTEGER DEFAULT 0,

    field_goals_made INTEGER DEFAULT 0,
    field_goals_attempted INTEGER DEFAULT 0,
    three_pointers_made INTEGER DEFAULT 0,
    three_pointers_attempted INTEGER DEFAULT 0,
    free_throws_made INTEGER DEFAULT 0,
    free_throws_attempted INTEGER DEFAULT 0,
    
    minutes_played FLOAT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_player_game UNIQUE (player_id, game_id)
);

-- Player indexes
CREATE INDEX idx_players_name ON players(name);
CREATE INDEX idx_players_team ON players(team);
CREATE INDEX idx_players_position ON players(position);

-- Game indexes
CREATE INDEX idx_games_date ON games(game_date);
CREATE INDEX idx_games_season ON games(season);
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_games_home_team ON games(home_team);
CREATE INDEX idx_games_away_team ON games(away_team);

-- Stats indexes
CREATE INDEX idx_stats_player ON player_stats(player_id);
CREATE INDEX idx_stats_game ON player_stats(game_id);
CREATE INDEX idx_stats_points ON player_stats(points);

-- Player Season Averages View
CREATE OR REPLACE VIEW player_season_averages AS
SELECT 
    p.id as player_id,
    p.name,
    p.team,
    p.position,
    g.season,
    COUNT(ps.id) as games_played,
    ROUND(AVG(ps.points), 1) as avg_points,
    ROUND(AVG(ps.assists), 1) as avg_assists,
    ROUND(AVG(ps.rebounds), 1) as avg_rebounds,
    ROUND(AVG(ps.steals), 1) as avg_steals,
    ROUND(AVG(ps.blocks), 1) as avg_blocks,
    ROUND(AVG(ps.minutes_played), 1) as avg_minutes,
    ROUND(
        CASE 
            WHEN SUM(ps.field_goals_attempted) > 0 
            THEN (SUM(ps.field_goals_made)::FLOAT / SUM(ps.field_goals_attempted)) * 100
            ELSE 0 
        END, 1
    ) as field_goal_pct,
    ROUND(
        CASE 
            WHEN SUM(ps.three_pointers_attempted) > 0 
            THEN (SUM(ps.three_pointers_made)::FLOAT / SUM(ps.three_pointers_attempted)) * 100
            ELSE 0 
        END, 1
    ) as three_point_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
JOIN games g ON ps.game_id = g.id
GROUP BY p.id, p.name, p.team, p.position, g.season;

-- Team Stats View
CREATE OR REPLACE VIEW team_stats AS
SELECT 
    p.team,
    g.season,
    COUNT(DISTINCT p.id) as total_players,
    COUNT(ps.id) as total_games,
    ROUND(AVG(ps.points), 1) as avg_points_per_player,
    ROUND(AVG(ps.assists), 1) as avg_assists_per_player,
    ROUND(AVG(ps.rebounds), 1) as avg_rebounds_per_player
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
JOIN games g ON ps.game_id = g.id
GROUP BY p.team, g.season;

-- Get top scorers
SELECT 
    p.name, 
    p.team,
    ROUND(AVG(ps.points), 1) as avg_points,
    COUNT(ps.id) as games_played
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
GROUP BY p.id, p.name, p.team
ORDER BY avg_points DESC
LIMIT 10;

-- Get player season stats
SELECT * FROM player_season_averages 
WHERE player_id = 1 AND season = '2024-2025';

-- Get team performance
SELECT * FROM team_stats 
WHERE team = 'Lakers' AND season = '2024-2025';

-- Get game box score
SELECT 
    p.name,
    p.team,
    ps.points,
    ps.assists,
    ps.rebounds,
    ps.field_goals_made || '/' || ps.field_goals_attempted as fg,
    ps.three_pointers_made || '/' || ps.three_pointers_attempted as three_pt,
    ps.minutes_played as minutes
FROM player_stats ps
JOIN players p ON ps.player_id = p.id
WHERE ps.game_id = 1
ORDER BY ps.points DESC;