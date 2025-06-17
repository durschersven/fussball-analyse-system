import argparse

from .database import SessionLocal, init_db
from .data_ingest import (
    load_teams,
    load_players,
    load_matches,
    load_teams_df,
    load_players_df,
    load_matches_df,
)
from .self_learning import self_improve
from . import demo as demo_module
from . import auto_update


def main():
    parser = argparse.ArgumentParser(description="Fussball Analyse System")
    sub = parser.add_subparsers(dest="command")

    ing = sub.add_parser("ingest", help="Load CSV data")
    ing.add_argument("type", choices=["teams", "players", "matches"])
    ing.add_argument("csv_file")

    sub.add_parser("train", help="Train and predict")
    sub.add_parser("demo", help="Fetch online data and run demo training")
    sub.add_parser("sync", help="Download latest results and update database")
    sub.add_parser("pipeline", help="Sync data and train in one step")

    args = parser.parse_args()
    init_db()
    session = SessionLocal()

    if args.command == "ingest":
        if args.type == "teams":
            load_teams(session, args.csv_file)
        elif args.type == "players":
            load_players(session, args.csv_file)
        elif args.type == "matches":
            load_matches(session, args.csv_file)
    elif args.command == "train":
        self_improve(session)
    elif args.command == "demo":
        demo_module.run_demo(session)
    elif args.command == "sync":
        auto_update.sync_data(session)
    elif args.command == "pipeline":
        auto_update.sync_data(session)
        self_improve(session)

    session.close()


if __name__ == "__main__":
    main()
