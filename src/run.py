#!/usr/bin/env python3
"""
BUDDHA PROJECT
Aviation Crash Analytics Dashboard

Advanced launcher script for initializing, validating,
and running the Streamlit dashboard in a production-like setup.
"""

import subprocess
import sys
import os
import time
import json
import platform
from typing import List, Optional

# -----------------------------
# Global Configuration
# -----------------------------

MIN_PYTHON_VERSION = (3, 8)
DASHBOARD_PORT = 8501
STREAMLIT_APP_PATH = os.path.join("src", "streamlit_app.py")
REQUIREMENTS_FILE = "requirements.txt"

DATASET_CANDIDATES = [
    os.path.join("data", "dataset.csv.csv"),
    os.path.join("data", "dataset.csv"),
    "dataset.csv.csv",
    "dataset.csv",
]

RUNTIME_STATE_FILE = ".runtime_state.json"


# -----------------------------
# Utility & Logging
# -----------------------------

def log(message: str, level: str = "INFO") -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def save_runtime_state(state: dict) -> None:
    try:
        with open(RUNTIME_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except IOError:
        log("Failed to save runtime state", "WARN")


def load_runtime_state() -> dict:
    if not os.path.exists(RUNTIME_STATE_FILE):
        return {}
    try:
        with open(RUNTIME_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


# -----------------------------
# Environment Checks
# -----------------------------

def check_python_version() -> None:
    log("Checking Python version")
    if sys.version_info < MIN_PYTHON_VERSION:
        log(
            f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ required. "
            f"Found {sys.version.split()[0]}",
            "ERROR",
        )
        sys.exit(1)

    log(f"Python version OK: {sys.version.split()[0]}")


def detect_operating_system() -> str:
    os_name = platform.system()
    log(f"Detected OS: {os_name}")
    return os_name


def verify_virtual_environment() -> None:
    if hasattr(sys, "real_prefix") or sys.prefix != sys.base_prefix:
        log("Running inside a virtual environment")
    else:
        log("Virtual environment not detected (recommended)", "WARN")


# -----------------------------
# Dependency Management
# -----------------------------

def install_dependencies() -> None:
    log("Installing project dependencies")
    if not os.path.exists(REQUIREMENTS_FILE):
        log("requirements.txt not found", "ERROR")
        sys.exit(1)

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE]
        )
        log("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        log("Dependency installation failed", "ERROR")
        sys.exit(1)


def ensure_streamlit_installed() -> None:
    try:
        import streamlit  # noqa: F401
        log("Streamlit already installed")
    except ImportError:
        log("Streamlit not found, installing now")
        install_dependencies()


# -----------------------------
# Dataset Validation
# -----------------------------

def find_dataset_file(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def check_dataset() -> str:
    log("Validating dataset availability")
    dataset_path = find_dataset_file(DATASET_CANDIDATES)

    if not dataset_path:
        log("No valid dataset file found", "ERROR")
        for p in DATASET_CANDIDATES:
            log(f"Checked: {p}", "DEBUG")
        sys.exit(1)

    log(f"Dataset found at: {dataset_path}")
    return dataset_path


# -----------------------------
# Dashboard Runner
# -----------------------------

def run_dashboard() -> None:
    log("Launching Streamlit dashboard")
    log(f"Dashboard URL: http://localhost:{DASHBOARD_PORT}")
    log("Press Ctrl+C to stop")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                STREAMLIT_APP_PATH,
                "--server.port",
                str(DASHBOARD_PORT),
            ],
            check=False,
        )
    except KeyboardInterrupt:
        log("Dashboard stopped by user")
    except FileNotFoundError:
        log("Streamlit command failed. Retrying after install", "WARN")
        install_dependencies()
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", STREAMLIT_APP_PATH],
            check=False,
        )


# -----------------------------
# Main Entry Point
# -----------------------------

def main() -> None:
    print("=" * 60)
    print("✈️  BUDDHA PROJECT - Aviation Crash Analytics Dashboard")
    print("=" * 60)

    runtime_state = load_runtime_state()

    check_python_version()
    detect_operating_system()
    verify_virtual_environment()

    dataset_path = check_dataset()
    ensure_streamlit_installed()

    runtime_state.update(
        {
            "last_run": time.time(),
            "dataset": dataset_path,
            "python": sys.version.split()[0],
        }
    )
    save_runtime_state(runtime_state)

    run_dashboard()


if __name__ == "__main__":
    main()
