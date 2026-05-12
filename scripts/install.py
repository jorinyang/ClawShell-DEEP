#!/usr/bin/env python3
"""ClawShell 2.0 — Install script"""
import subprocess, sys
from pathlib import Path

def main():
    print("ClawShell 2.0 — Install")
    if sys.version_info < (3, 10): print("ERROR: Python >= 3.10 required"); sys.exit(1)
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} OK")
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=Path(__file__).parent.parent, check=True)
        print("Dependencies installed")
    except subprocess.CalledProcessError:
        print("ERROR: install failed"); sys.exit(1)
    for d in ["data/eventbus", "data/knowledge", "data/memory", "config", "plugins"]:
        (Path(__file__).parent.parent / d).mkdir(parents=True, exist_ok=True)
    print("ClawShell 2.0 installed!")
    print("  clawshell init      # generate config")
    print("  clawshell cortex    # start cortex")
    print("  clawshell ganglion  # start ganglion")

if __name__ == "__main__": main()
