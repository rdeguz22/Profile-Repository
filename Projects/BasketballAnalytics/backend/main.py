from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db, engine, Base, mongodb
from models import Player, PlayerStats, Game
from schemas import (
    PlayerCreate, PlayerResponse, PlayerUpdate,
    StatsCreate, StatsResponse,
    GameCreate, GameResponse, GameUpdate,
    GameEventCreate, GameEventResponse
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Basketball Platform API",
    description="Simple basketball management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# ROOT ENDPOINT
# ========================================

@app.get("/")
def read_root():
    """API information"""
    return {
        "message": "Basketball Platform API",
        "version": "1.0.0",
        "databases": {
            "postgresql": "Player/Game data & statistics",
            "mongodb": "Real-time game events",
            "pinecone": "Player similarity search (optional)"
        },
        "endpoints": {
            "players": "/api/players",
            "games": "/api/games",
            "stats": "/api/stats",
            "docs": "/docs"
        }
    }

# ========================================
# PLAYER ENDPOINTS
# ========================================

@app.post("/api/players", response_model=PlayerResponse, status_code=201)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Create a new player"""
    db_player = Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/api/players", response_model=List[PlayerResponse])
def get_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    team: Optional[str] = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all players with optional filters"""
    query = db.query(Player)
    
    if team:
        query = query.filter(Player.team == team)
    if position:
        query = query.filter(Player.position == position)
    
    players = query.offset(skip).limit(limit).all()
    return players

@app.get("/api/players/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get player by ID"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.put("/api/players/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, player_update: PlayerUpdate, db: Session = Depends(get_db)):
    """Update player information"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    for key, value in player_update.dict(exclude_unset=True).items():
        setattr(player, key, value)
    
    db.commit()
    db.refresh(player)
    return player

@app.delete("/api/players/{player_id}")
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """Delete player"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    db.delete(player)
    db.commit()
    return {"message": "Player deleted successfully"}

@app.get("/api/players/{player_id}/stats")
def get_player_stats(player_id: int, season: Optional[str] = None, db: Session = Depends(get_db)):
    """Get player statistics"""
    query = db.query(PlayerStats).filter(PlayerStats.player_id == player_id)
    
    if season:
        query = query.join(Game).filter(Game.season == season)
    
    stats = query.all()
    
    if not stats:
        return {"total_games": 0, "averages": {}}
    
    total_games = len(stats)
    
    # Calculate totals
    totals = {
        'points': sum(s.points for s in stats),
        'assists': sum(s.assists for s in stats),
        'rebounds': sum(s.rebounds for s in stats),
        'steals': sum(s.steals for s in stats),
        'blocks': sum(s.blocks for s in stats),
        'turnovers': sum(s.turnovers for s in stats),
        'field_goals_made': sum(s.field_goals_made for s in stats),
        'field_goals_attempted': sum(s.field_goals_attempted for s in stats),
        'three_pointers_made': sum(s.three_pointers_made for s in stats),
        'three_pointers_attempted': sum(s.three_pointers_attempted for s in stats),
        'minutes_played': sum(s.minutes_played for s in stats)
    }
    
    # Calculate averages
    averages = {
        'points': round(totals['points'] / total_games, 1),
        'assists': round(totals['assists'] / total_games, 1),
        'rebounds': round(totals['rebounds'] / total_games, 1),
        'steals': round(totals['steals'] / total_games, 1),
        'blocks': round(totals['blocks'] / total_games, 1),
        'turnovers': round(totals['turnovers'] / total_games, 1),
        'field_goal_pct': round((totals['field_goals_made'] / totals['field_goals_attempted'] * 100), 1) if totals['field_goals_attempted'] > 0 else 0,
        'three_point_pct': round((totals['three_pointers_made'] / totals['three_pointers_attempted'] * 100), 1) if totals['three_pointers_attempted'] > 0 else 0,
        'minutes': round(totals['minutes_played'] / total_games, 1)
    }
    
    return {
        "total_games": total_games,
        "totals": totals,
        "averages": averages
    }

@app.get("/api/players/{player_id}/similar")
async def find_similar_players(player_id: int, top_k: int = 5):
    """Find similar players using Pinecone vector similarity"""
    return {
        "message": "Player similarity search - requires Pinecone configuration",
        "player_id": player_id,
        "note": "Configure Pinecone API key to enable this feature"
    }

# ========================================
# GAME ENDPOINTS
# ========================================

@app.post("/api/games", response_model=GameResponse, status_code=201)
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    """Create a new game"""
    db_game = Game(**game.dict(), status="scheduled")
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

@app.get("/api/games", response_model=List[GameResponse])
def get_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    season: Optional[str] = None,
    status: Optional[str] = None,
    team: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all games with optional filters"""
    query = db.query(Game)
    
    if season:
        query = query.filter(Game.season == season)
    if status:
        query = query.filter(Game.status == status)
    if team:
        query = query.filter((Game.home_team == team) | (Game.away_team == team))
    
    games = query.order_by(Game.game_date.desc()).offset(skip).limit(limit).all()
    return games

@app.get("/api/games/{game_id}", response_model=GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get game by ID"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.put("/api/games/{game_id}", response_model=GameResponse)
def update_game(game_id: int, game_update: GameUpdate, db: Session = Depends(get_db)):
    """Update game information"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    for key, value in game_update.dict(exclude_unset=True).items():
        setattr(game, key, value)
    
    db.commit()
    db.refresh(game)
    return game

@app.delete("/api/games/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """Delete game"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    db.delete(game)
    db.commit()
    return {"message": "Game deleted successfully"}

@app.post("/api/games/{game_id}/stats", response_model=StatsResponse, status_code=201)
def add_game_stats(game_id: int, stats: StatsCreate, db: Session = Depends(get_db)):
    """Add player stats for a game"""
    # Verify game exists
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Verify player exists
    player = db.query(Player).filter(Player.id == stats.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    db_stats = PlayerStats(**stats.dict())
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats

@app.get("/api/games/{game_id}/stats")
def get_game_stats(game_id: int, db: Session = Depends(get_db)):
    """Get all player stats for a game"""
    stats = db.query(PlayerStats, Player.name).join(Player).filter(
        PlayerStats.game_id == game_id
    ).all()
    
    return [
        {
            "player_name": player_name,
            "points": stat.points,
            "assists": stat.assists,
            "rebounds": stat.rebounds,
            "steals": stat.steals,
            "blocks": stat.blocks,
            "turnovers": stat.turnovers,
            "field_goals": f"{stat.field_goals_made}/{stat.field_goals_attempted}",
            "three_pointers": f"{stat.three_pointers_made}/{stat.three_pointers_attempted}",
            "free_throws": f"{stat.free_throws_made}/{stat.free_throws_attempted}",
            "minutes": stat.minutes_played
        }
        for stat, player_name in stats
    ]

# ========================================
# GAME EVENTS (MongoDB)
# ========================================

@app.post("/api/games/{game_id}/events")
async def create_game_event(game_id: int, event: GameEventCreate):
    """Create a real-time game event"""
    event_data = {
        **event.dict(),
        "timestamp": datetime.utcnow(),
        "game_id": game_id
    }
    
    result = await mongodb.game_events.insert_one(event_data)
    event_data["id"] = str(result.inserted_id)
    event_data["_id"] = str(result.inserted_id)
    
    return event_data

@app.get("/api/games/{game_id}/events")
async def get_game_events(game_id: int):
    """Get all events for a specific game"""
    events = []
    cursor = mongodb.game_events.find({"game_id": game_id}).sort("timestamp", 1)
    
    async for event in cursor:
        event["_id"] = str(event["_id"])
        event["id"] = str(event["_id"])
        events.append(event)
    
    return events

# ========================================
# BASIC STATISTICS ENDPOINTS
# ========================================

@app.get("/api/stats/top-scorers")
def get_top_scorers(limit: int = Query(10, le=50), season: Optional[str] = None, db: Session = Depends(get_db)):
    """Get top scorers"""
    query = db.query(
        Player.id,
        Player.name,
        Player.team,
        func.avg(PlayerStats.points).label('avg_points'),
        func.count(PlayerStats.id).label('games_played')
    ).join(PlayerStats)
    
    if season:
        query = query.join(Game).filter(Game.season == season)
    
    results = query.group_by(Player.id).order_by(
        func.avg(PlayerStats.points).desc()
    ).limit(limit).all()
    
    return [
        {
            'player_id': r.id,
            'name': r.name,
            'team': r.team,
            'avg_points': round(r.avg_points, 1),
            'games_played': r.games_played
        }
        for r in results
    ]

@app.get("/api/stats/team")
def get_team_stats(team: str, season: Optional[str] = None, db: Session = Depends(get_db)):
    """Get aggregated stats for a team"""
    query = db.query(
        func.avg(PlayerStats.points).label('avg_points'),
        func.avg(PlayerStats.assists).label('avg_assists'),
        func.avg(PlayerStats.rebounds).label('avg_rebounds'),
        func.count(PlayerStats.id).label('total_games')
    ).join(Player).filter(Player.team == team)
    
    if season:
        query = query.join(Game).filter(Game.season == season)
    
    results = query.first()
    
    if not results or results.total_games == 0:
        raise HTTPException(status_code=404, detail="No data found for team")
    
    return {
        'team': team,
        'season': season if season else 'all',
        'avg_points': round(results.avg_points or 0, 1),
        'avg_assists': round(results.avg_assists or 0, 1),
        'avg_rebounds': round(results.avg_rebounds or 0, 1),
        'total_games': results.total_games
    }

@app.get("/api/stats/leaderboard")
def get_leaderboard(
    stat: str = Query("points", regex="^(points|assists|rebounds|steals|blocks)$"),
    limit: int = Query(10, le=50),
    season: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get leaderboard for any stat"""
    stat_column = getattr(PlayerStats, stat)
    
    query = db.query(
        Player.name,
        Player.team,
        func.avg(stat_column).label(f'avg_{stat}'),
        func.count(PlayerStats.id).label('games_played')
    ).join(PlayerStats).join(Game)
    
    if season:
        query = query.filter(Game.season == season)
    
    results = query.group_by(Player.id).order_by(
        func.avg(stat_column).desc()
    ).limit(limit).all()
    
    return [
        {
            'name': r.name,
            'team': r.team,
            f'avg_{stat}': round(getattr(r, f'avg_{stat}'), 1),
            'games_played': r.games_played
        }
        for r in results
    ]

# ========================================
# HEALTH CHECK
# ========================================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }

# ========================================
# RUN APPLICATION
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)