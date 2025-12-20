#!/usr/bin/env python3
"""
BUDDHA PROJECT - Aviation Crash Analytics Dashboard
Simple launcher script for the Streamlit dashboard
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        sys.exit(1)

def check_dataset():
    """Check if dataset file exists"""
    if not os.path.exists("data\dataset.csv.csv"):
        print("❌ Error: dataset.csv.csv not found")
        print("Please ensure the dataset file is in the project directory")
        sys.exit(1)
    print("✅ Dataset file found")

def run_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching BUDDHA Aviation Dashboard...")
    print("🌐 Dashboard will open at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thank you for using BUDDHA PROJECT!")
    except FileNotFoundError:
        print("❌ Error: Streamlit not installed. Installing...")
        install_dependencies()
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/streamlit_app.py"])

def main():
    """Main launcher function"""
    print("=" * 50)
    print("✈️  BUDDHA PROJECT - Aviation Analytics Dashboard")
    print("=" * 50)
    
    # Check prerequisites
    check_python_version()
    check_dataset()
    
    # Install dependencies if needed
    try:
        import streamlit
        print("✅ Streamlit already installed")
    except ImportError:
        install_dependencies()
    
    # Launch dashboard
    run_dashboard()

if __name__ == "__main__":
    main()