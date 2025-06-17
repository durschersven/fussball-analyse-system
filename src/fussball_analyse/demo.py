import io
from typing import Dict

import pandas as pd
import requests
from sqlalchemy.orm import Session

from .data_ingest import load_teams_df, load_players_df, load_matches_df
from .models import Match, Team
from .self_learning import self_improve


MATCHES_URL = "https://www.football-data.co.uk/mmz4281/2122/E0.csv"
PLAYERS_URL = (
    "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2021-22/players_raw.csv"
)
TEAMS_URL = (
    "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2021-22/teams.csv"
)

TEAM_NAME_MAP = {"Man Utd": "Man United", "Spurs": "Tottenham"}


def fetch_csv(url: str) -> pd.DataFrame:
    """Download a CSV file into a DataFrame."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text))


def run_demo(session: Session) -> None:
    """Fetch sample data, train and evaluate on a small holdout set."""
    matches_df = fetch_csv(MATCHES_URL)
    teams_df = fetch_csv(TEAMS_URL)
    players_df = fetch_csv(PLAYERS_URL)

    teams_df["name"] = teams_df["name"].replace(TEAM_NAME_MAP)
    load_teams_df(session, teams_df[["name"]])

    team_map: Dict[str, int] = {t.name: t.id for t in session.query(Team).all()}
    players_df["team"] = players_df["team"].map(lambda x: teams_df.loc[x - 1, "name"])  # team is index
    players_df["team"] = players_df["team"].replace(TEAM_NAME_MAP)
    load_players_df(session, players_df, team_map)

    matches_df["Date"] = pd.to_datetime(matches_df["Date"], dayfirst=True)
    matches_df = matches_df.sort_values("Date")
    holdout = matches_df.tail(10)
    train_df = matches_df.iloc[:-10]

    def convert(df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "date": df["Date"],
                "home_team": df["HomeTeam"].replace(TEAM_NAME_MAP),
                "away_team": df["AwayTeam"].replace(TEAM_NAME_MAP),
                "home_goals": df.get("FTHG"),
                "away_goals": df.get("FTAG"),
            }
        )

    load_matches_df(session, convert(train_df), team_map)
    # holdout matches without results
    holdout_nores = convert(holdout)
    holdout_nores["home_goals"] = None
    holdout_nores["away_goals"] = None
    load_matches_df(session, holdout_nores, team_map)

    print("Initial training and prediction on holdout matches:")
    self_improve(session)

    # reveal actual results
    holdout_matches = (
        session.query(Match).filter(Match.home_goals == None).order_by(Match.date).all()
    )
    for match_obj, (_, row) in zip(holdout_matches, holdout.iterrows()):
        match_obj.home_goals = int(row["FTHG"])
        match_obj.away_goals = int(row["FTAG"])
    session.commit()

    print("\nAfter adding actual results:")
    self_improve(session)
