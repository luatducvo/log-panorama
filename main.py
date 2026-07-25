import subprocess
import sys


def main() -> None:
    try:
        subprocess.run(
            ["streamlit", "run", "app.py", "--server.headless", "true"],
            check=True,
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    sys.exit(main())
