from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .database import Base

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    players = relationship('Player', back_populates='team')
    elo = Column(Float, default=1000.0)


class League(Base):
    __tablename__ = 'leagues'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    position = Column(String)
    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship('Team', back_populates='players')

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    season = Column(String)
    league_id = Column(Integer, ForeignKey('leagues.id'))
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    home_goals = Column(Integer)
    away_goals = Column(Integer)

class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    score = Column(Float)


class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    predicted_result = Column(Integer)  # 1=home win, 0=draw, -1=away win
    actual_result = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    match = relationship('Match')
