from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    team = Column(String, nullable=False)
    position = Column(String, nullable=False)
    height = Column(Float, nullable=False)  # in inches
    weight = Column(Float, nullable=False)  # in pounds
    jersey_number = Column(Integer, nullable=False)
    birth_date = Column(Date, nullable=False)
    
    stats = relationship("PlayerStats", back_populates="player", cascade="all, delete-orphan")

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    game_date = Column(Date, nullable=False)
    season = Column(String, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed
    
    stats = relationship("PlayerStats", back_populates="game", cascade="all, delete-orphan")

class PlayerStats(Base):
    __tablename__ = "player_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    
    points = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    rebounds = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    fouls = Column(Integer, default=0)

    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    three_pointers_made = Column(Integer, default=0)
    three_pointers_attempted = Column(Integer, default=0)
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)

    minutes_played = Column(Float, default=0)
    
    player = relationship("Player", back_populates="stats")
    game = relationship("Game", back_populates="stats")