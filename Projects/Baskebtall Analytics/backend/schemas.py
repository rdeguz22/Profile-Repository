from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

# PLAYER SCHEMAS
class PlayerBase(BaseModel):
    name: str
    team: str
    position: str
    height: float
    weight: float
    jersey_number: int
    birth_date: date

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    team: Optional[str] = None
    position: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    jersey_number: Optional[int] = None

class PlayerResponse(PlayerBase):
    id: int
    
    class Config:
        from_attributes = True

# STATS SCHEMAS
class StatsBase(BaseModel):
    player_id: int
    game_id: int
    points: int = 0
    assists: int = 0
    rebounds: int = 0
    steals: int = 0
    blocks: int = 0
    turnovers: int = 0
    fouls: int = 0
    field_goals_made: int = 0
    field_goals_attempted: int = 0
    three_pointers_made: int = 0
    three_pointers_attempted: int = 0
    free_throws_made: int = 0
    free_throws_attempted: int = 0
    minutes_played: float = 0

class StatsCreate(StatsBase):
    pass

class StatsResponse(StatsBase):
    id: int
    
    class Config:
        from_attributes = True

# GAME SCHEMAS
class GameBase(BaseModel):
    home_team: str
    away_team: str
    game_date: date
    season: str

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[str] = None

class GameResponse(GameBase):
    id: int
    home_score: int
    away_score: int
    status: str
    
    class Config:
        from_attributes = True

# EVENT SCHEMAS (MongoDB)
class GameEventCreate(BaseModel):
    game_id: int
    event_type: str
    player_id: int
    player_name: str
    team: str
    quarter: int
    time_remaining: str
    description: str

class GameEventResponse(GameEventCreate):
    id: str
    timestamp: datetime