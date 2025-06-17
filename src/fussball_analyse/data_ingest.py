import pandas as pd
from sqlalchemy.orm import Session

from .models import Team, Player, Match, League


def load_teams(session: Session, csv_file: str):
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        team = Team(name=row['name'])
        session.add(team)
    session.commit()


def load_leagues(session: Session, csv_file: str):
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        league = League(code=row['code'], name=row['name'])
        session.add(league)
    session.commit()


def load_players(session: Session, csv_file: str):
    df = pd.read_csv(csv_file)
    for _, row in df.iterrows():
        player = Player(name=row['name'], position=row.get('position'), team_id=row.get('team_id'))
        session.add(player)
    session.commit()


def load_matches(session: Session, csv_file: str):
    df = pd.read_csv(csv_file, parse_dates=['date'])
    for _, row in df.iterrows():
        match = Match(
            date=row['date'],
            season=row.get('season'),
            league_id=row.get('league_id'),
            home_team_id=row['home_team_id'],
            away_team_id=row['away_team_id'],
            home_goals=row.get('home_goals'),
            away_goals=row.get('away_goals'),
        )
        session.add(match)
    session.commit()


def load_teams_df(session: Session, df: pd.DataFrame):
    for _, row in df.iterrows():
        team = Team(name=row["name"])
        session.add(team)
    session.commit()


def load_leagues_df(session: Session, df: pd.DataFrame):
    for _, row in df.iterrows():
        league = League(code=row["code"], name=row["name"])
        session.add(league)
    session.commit()


def load_players_df(session: Session, df: pd.DataFrame, team_map: dict[str, int]):
    for _, row in df.iterrows():
        team_name = row.get("team")
        team_id = team_map.get(team_name)
        player = Player(
            name=f"{row.get('first_name', '')} {row.get('second_name', '')}".strip(),
            position=row.get("position"),
            team_id=team_id,
        )
        session.add(player)
    session.commit()


def load_matches_df(session: Session, df: pd.DataFrame, team_map: dict[str, int]):
    for _, row in df.iterrows():
        match = Match(
            date=row["date"],
            season=row.get("season"),
            league_id=row.get("league_id"),
            home_team_id=team_map.get(row["home_team"]),
            away_team_id=team_map.get(row["away_team"]),
            home_goals=row.get("home_goals"),
            away_goals=row.get("away_goals"),
        )
        session.add(match)
    session.commit()
