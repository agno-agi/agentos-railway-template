"""Run Scout agent from the command line: python -m scout"""

from scout.agent import scout

if __name__ == "__main__":
    scout.cli_app(stream=True)
