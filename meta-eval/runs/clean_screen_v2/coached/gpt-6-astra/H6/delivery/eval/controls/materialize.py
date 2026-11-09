"""Generate a standalone positive or negative control in a new directory."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def materialize(mode, destination):
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    modes = set(manifest["positives"]) | {item["mode"] for item in manifest["negatives"]}
    if mode not in modes:
        raise ValueError("unknown mode: " + mode)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    source = (HERE / "correct" / "summarize.py").read_text(encoding="utf-8")
    assert source.endswith("    main()\n")
    source = source.removesuffix("    main()\n") + f"    main({mode!r})\n"
    (destination / "summarize.py").write_text(source, encoding="utf-8")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    materialize(args.mode, args.destination)
