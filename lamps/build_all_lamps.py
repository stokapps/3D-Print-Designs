#!/usr/bin/env python3
"""
Blender Automation Script for Lamp Generation
This script automatically detects and runs lamp generation scripts in Blender to generate STL files.
Only regenerates STLs for files that have changed since last run.
"""

import os
import subprocess
import platform
import sys
import hashlib
import json
import re
from datetime import datetime

# Cache file to store file hashes
HASH_CACHE_FILE = ".lamp_build_cache.json"

# Patterns for identifying lamp scripts and extracting STL names
LAMP_SCRIPT_PATTERN = r"^(lamp_.*|.*_lamp_.*|simple_.*lamp.*)\.py$"
BASE_SCRIPT_NAME = "lamp_base.py"  # Special case for the base

def find_lamp_scripts(directory):
    """Find all lamp-related Python scripts in the given directory"""
    scripts = []
    for filename in os.listdir(directory):
        if filename.endswith('.py') and (re.match(LAMP_SCRIPT_PATTERN, filename) or filename == BASE_SCRIPT_NAME):
            scripts.append(filename)
    return sorted(scripts)

def determine_stl_filename(script_path):
    """Parse the script to find the STL output filename or derive from script name"""
    # First, try to extract from export_filepath in the script
    try:
        with open(script_path, 'r') as file:
            content = file.read()
            # Look for export filepath definition in the script
            match = re.search(r'export_filepath\s*=.*?[\'"].*?\/([^\/]+\.stl)[\'"]', content, re.DOTALL)
            if match:
                return match.group(1)
    except (IOError, UnicodeDecodeError):
        pass
    
    # If extraction fails, derive from script name
    script_name = os.path.basename(script_path)
    base_name = os.path.splitext(script_name)[0]
    
    # For other scripts, transform script name to STL name
    # Remove 'lamp_' prefix if present, otherwise remove '_lamp' suffix
    if base_name.startswith("lamp_"):
        stl_name = base_name[5:]
    elif "_lamp" in base_name:
        stl_name = base_name.replace("_lamp", "")
    else:
        stl_name = base_name
    
    # Ensure "shade" is in the name if it's not a base
    if "shade" not in stl_name.lower() and "base" not in stl_name.lower():
        stl_name += "_shade"
    
    return f"{stl_name}.stl"

def calculate_file_hash(file_path):
    """Calculate the MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError:
        return None

def load_hash_cache(cache_path):
    """Load the hash cache from disk"""
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {}
    return {}

def save_hash_cache(cache_path, cache_data):
    """Save the hash cache to disk"""
    try:
        with open(cache_path, "w") as f:
            json.dump(cache_data, f, indent=2)
        return True
    except IOError:
        print(f"Warning: Could not save hash cache to {cache_path}")
        return False

def find_blender_path():
    """Find the Blender executable path based on OS"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Common macOS Blender paths
        possible_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender"),
            # Blender 4.0
            "/Applications/Blender.app/Contents/MacOS/blender",
            os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/blender"),
        ]
    elif system == "Windows":
        # Common Windows Blender paths
        possible_paths = [
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        ]
    else:  # Linux
        # Try using the system blender
        possible_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If we can't find Blender, ask the user
    print("Could not automatically find Blender executable.")
    manual_path = input("Please enter the full path to your Blender executable: ")
    
    if os.path.exists(manual_path):
        return manual_path
    else:
        raise FileNotFoundError(f"Could not find Blender executable at {manual_path}")

def run_blender_script(blender_path, script_path):
    """Run a Python script in Blender headless mode"""
    abs_script_path = os.path.abspath(script_path)
    
    # Make sure script exists
    if not os.path.exists(abs_script_path):
        print(f"Error: Script file not found: {abs_script_path}")
        return False
    
    print(f"Running Blender with script: {os.path.basename(script_path)}")
    
    # Run Blender in background mode with the script
    try:
        process = subprocess.run([
            blender_path,
            "--background",  # Run Blender in headless mode
            "--python", abs_script_path  # Script to execute
        ], 
        check=True,
        capture_output=True,
        text=True)
        
        # Print output
        print("---- Output ----")
        print(process.stdout)
        
        if process.stderr:
            print("---- Errors ----")
            print(process.stderr)
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error running Blender: {e}")
        if e.stdout:
            print("---- Output ----")
            print(e.stdout)
        if e.stderr:
            print("---- Errors ----")
            print(e.stderr)
        return False

def main():
    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change working directory to the script directory
    os.chdir(script_dir)
    
    # Ensure STLs directory exists
    stl_dir = os.path.join(script_dir, "STLs")
    if not os.path.exists(stl_dir):
        os.makedirs(stl_dir)
        print(f"Created STLs directory: {stl_dir}")
    
    # Find all lamp scripts in the directory
    all_scripts = find_lamp_scripts(script_dir)
    print(f"Found {len(all_scripts)} lamp scripts: {', '.join(all_scripts)}")
    
    # Dynamically build the script-to-STL mapping
    script_to_stl = {}
    for script in all_scripts:
        script_path = os.path.join(script_dir, script)
        stl_filename = determine_stl_filename(script_path)
        script_to_stl[script] = stl_filename
    
    print("Script to STL mapping:")
    for script, stl in script_to_stl.items():
        print(f"  {script} -> {stl}")
    
    # Load the hash cache
    cache_path = os.path.join(script_dir, HASH_CACHE_FILE)
    hash_cache = load_hash_cache(cache_path)
    
    # Find Blender executable
    try:
        blender_path = find_blender_path()
        print(f"Found Blender at: {blender_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Track current file hashes and which files need processing
    current_hashes = {}
    files_processed = []
    
    # Process each script
    for script in all_scripts:
        script_path = os.path.join(script_dir, script)
        
        # Skip if file doesn't exist (shouldn't happen since we just found it)
        if not os.path.exists(script_path):
            print(f"Warning: Script file not found: {script_path}")
            continue
        
        # Calculate the current hash of the script
        current_hash = calculate_file_hash(script_path)
        current_hashes[script] = current_hash
        
        # Get the corresponding STL file
        stl_file = script_to_stl.get(script)
        stl_path = os.path.join(stl_dir, stl_file) if stl_file else None
        
        # Check if we need to process this script
        needs_processing = False
        
        # If the script isn't in the cache or its hash has changed
        if script not in hash_cache or hash_cache[script]["hash"] != current_hash:
            needs_processing = True
            reason = "modified" if script in hash_cache else "new"
        # Or if the STL file doesn't exist
        elif stl_file and not os.path.exists(stl_path):
            needs_processing = True
            reason = "missing STL"
        
        if needs_processing:
            print(f"Processing {script} (reason: {reason})")
            success = run_blender_script(blender_path, script_path)
            
            if success:
                print(f"✅ Successfully ran {script}")
                files_processed.append(script)
            else:
                print(f"❌ Failed to run {script}")
        else:
            print(f"⏩ Skipping {script} (unchanged since last run)")
    
    # Update the hash cache with new timestamps
    timestamp = datetime.now().isoformat()
    for script, file_hash in current_hashes.items():
        hash_cache[script] = {
            "hash": file_hash,
            "last_processed": timestamp if script in files_processed else 
                              hash_cache.get(script, {}).get("last_processed", timestamp)
        }
    
    # Save the updated hash cache
    save_hash_cache(cache_path, hash_cache)
    
    # Check all expected STL files
    print("\nChecking STL output files:")
    for script, stl_file in script_to_stl.items():
        stl_path = os.path.join(stl_dir, stl_file)
        if os.path.exists(stl_path):
            print(f"✅ Found STL: {stl_file}")
        else:
            print(f"❌ Missing STL: {stl_file}")

if __name__ == "__main__":
    main()
    print("\nDone! Check the STLs directory for your generated lamp models.")