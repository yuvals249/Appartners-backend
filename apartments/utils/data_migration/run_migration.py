#!/usr/bin/env python
"""
Script to run the Yad2 data migration process.
This script will:
1. Run the database migrations to add is_yad2 field and remove house_number
2. Import the Yad2 data into the database
"""

import os
import sys
import subprocess
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

def run_command(command, cwd=PROJECT_ROOT):
    """Run a shell command and print its output"""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=cwd
    )
    
    for line in process.stdout:
        print(line.strip())
    
    process.wait()
    return process.returncode

def run_migration():
    """Run the Yad2 data migration process"""
    print("Starting Yad2 data migration process")
    
    # Step 1: Run database migrations
    print("\n=== Running database migrations ===")
    result = run_command("python manage.py makemigrations")
    if result != 0:
        print("Error: Failed to create migrations")
        return
    
    result = run_command("python manage.py migrate")
    if result != 0:
        print("Error: Failed to apply migrations")
        return
    
    # Step 2: Import Yad2 data
    print("\n=== Importing Yad2 data ===")
    processed_file_path = os.path.join(PROJECT_ROOT, "apartments", "data", "processed_apartments.json")
    
    if not os.path.exists(processed_file_path):
        print(f"Error: Processed file {processed_file_path} does not exist!")
        print("Please run the yad2_parser.py and fill_missing_areas.py scripts first.")
        return
    
    # Import the data
    from import_yad2_data import import_yad2_data
    import_yad2_data(processed_file_path)
    
    print("\nYad2 data migration completed successfully!")

if __name__ == "__main__":
    run_migration()
