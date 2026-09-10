import time
import traceback

from src import config, teams_watch


def main() -> None:
    print(f"Polling every {config.POLL_INTERVAL_SECONDS}s. Ctrl+C to stop.")
    while True:
        try:
            teams_watch.poll_once()
        except Exception:
            traceback.print_exc()
        time.sleep(config.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
