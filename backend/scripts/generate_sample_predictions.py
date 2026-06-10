"""Compatibility wrapper for the V0.2 prediction pipeline."""

import generate_predictions
import normalize_matches


def main() -> None:
    normalize_matches.main()
    generate_predictions.main()


if __name__ == "__main__":
    main()
