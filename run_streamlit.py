#!/usr/bin/env python3
"""
Streamlit Application Launcher for CSV Analysis Agent

Run this script to start the web application:
python run_streamlit.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set environment variable for streamlit
    os.environ["PYTHONPATH"] = str(current_dir)
    
    # Path to the streamlit app
    app_path = current_dir / "app" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ Streamlit app not found at: {app_path}")
        return
    
    print("🚀 Starting CSV Analysis Agent Web Application...")
    print("📊 Opening in your default browser...")
    print("💡 To stop the server, press Ctrl+C")
    print("=" * 60)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path), 
            "--server.address", "localhost",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped. Thank you for using CSV Analysis Agent!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main() 