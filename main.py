import argparse
import logging

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel", default="WARNING", help="Loglevel", action="store"
    )
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise TypeError(f"Invalid log level: {args.loglevel}")
    logging.basicConfig(level=loglevel)


if __name__ == "__main__":
    main()
