"""Allow ``python -m ark`` to invoke the CLI."""

from ark.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
