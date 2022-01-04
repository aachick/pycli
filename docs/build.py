"""Build the documentation material. This is mainly to avoid consistency
issues between the documentation index file and the project's README.
"""
from pathlib import Path


CDIR = Path(__file__).parent
PROJECT_DIR = CDIR / ".."


def main():
    readme = (PROJECT_DIR / "README.md").read_text()
    (PROJECT_DIR / "docs" / "index.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
