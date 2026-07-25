import subprocess
import sys


def main() -> None:
    subprocess.run(
        ["streamlit", "run", "app.py", "--server.headless", "true"],
        check=True,
    )


if __name__ == "__main__":
    sys.exit(main())
