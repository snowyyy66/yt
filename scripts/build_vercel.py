"""Prepare the existing FastAPI static frontend for Vercel's static output."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app" / "static"
OUTPUT = ROOT / "vercel-dist"


def main() -> None:
    if not (SOURCE / "index.html").is_file():
        raise SystemExit(f"Frontend entry point is missing: {SOURCE / 'index.html'}")

    resolved_output = OUTPUT.resolve()
    if resolved_output.parent != ROOT.resolve() or resolved_output.name != "vercel-dist":
        raise SystemExit("Refusing to write outside the project vercel-dist directory")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "static").mkdir(parents=True)
    shutil.copy2(SOURCE / "index.html", OUTPUT / "index.html")

    for asset in SOURCE.iterdir():
        if asset.name == "index.html":
            continue
        destination = OUTPUT / "static" / asset.name
        if asset.is_dir():
            shutil.copytree(asset, destination)
        elif asset.is_file():
            shutil.copy2(asset, destination)

    print(f"Vercel static output prepared at {OUTPUT}")


if __name__ == "__main__":
    main()
