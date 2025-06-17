import io
from typing import Dict, List

import pandas as pd
import requests
from sqlalchemy.orm import Session

from .models import League, Team
from .data_ingest import load_matches_df

LEAGUE_CODES: Dict[str, str] = {
    "E0": "Premier League",
    "SP1": "La Liga",
    "I1": "Serie A",
    "D1": "Bundesliga",
    "F1": "Ligue 1",
}

BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"


def fetch_csv(url: str) -> pd.DataFrame | None:
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception:
        return None
    return pd.read_csv(io.StringIO(resp.text))


def get_or_create_league(session: Session, code: str, name: str) -> int:
    league = session.query(League).filter_by(code=code).first()
    if not league:
        league = League(code=code, name=name)
        session.add(league)
        session.commit()
    return league.id


def get_or_create_team(session: Session, name: str) -> int:
    team = session.query(Team).filter_by(name=name).first()
    if not team:
        team = Team(name=name)
        session.add(team)
        session.commit()
    return team.id


def sync_data(session: Session, seasons: List[str] | None = None) -> None:
    if seasons is None:
        seasons = ["2324"]
    for season in seasons:
        for code, name in LEAGUE_CODES.items():
            df = fetch_csv(BASE_URL.format(season=season, code=code))
            if df is None or df.empty:
                continue
            league_id = get_or_create_league(session, code, name)
            df = df.dropna(subset=["HomeTeam", "AwayTeam", "Date"])
            df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
            conv = pd.DataFrame(
                {
                    "date": df["Date"],
                    "home_team": df["HomeTeam"],
                    "away_team": df["AwayTeam"],
                    "home_goals": df.get("FTHG"),
                    "away_goals": df.get("FTAG"),
                    "league_id": league_id,
                    "season": season,
                }
            )
            # ensure teams exist
            team_map = {
                name: get_or_create_team(session, name)
                for name in pd.concat([conv["home_team"], conv["away_team"]]).unique()
            }
            load_matches_df(session, conv, team_map)

