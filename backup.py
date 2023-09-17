# ------------------------------
# Imports
# ------------------------------
import os
import shutil
import hashlib
import datetime

# List of source directories to be backed up
source_dirs = ['/home/peter/Pictures', '/home/peter/bash']
# Destination directory
backup_base_dir = '/home/peter/History'

# List of directories to be excluded from backup
excluded_dirs = ['/home/peter/Pictures/Windows Spotlight Images']

# Function to calculate the MD5 hash of a file
def calculate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

# Function to build a list of MD5 hashes from existing backup database files
def build_existing_hash_list(backup_base_dir):
    existing_hashes = set()  # Use a set for efficient lookup
    for root, _, files in os.walk(backup_base_dir):
        for file in files:
            if file.startswith("backup_database_") and file.endswith(".txt"):
                database_file = os.path.join(root, file)
                with open(database_file, 'r') as db:
                    lines = db.readlines()
                    for i in range(2, len(lines), 4):
                        md5_hash = lines[i].strip().split(": ")[1]
                        existing_hashes.add(md5_hash)
    return existing_hashes

# Function to perform an incremental backup
def incremental_backup(source_dirs, backup_base_dir):
    # Get the current date as a string (e.g., "2023-09-15")
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # Create a subdirectory with the current date in the backup base directory
    backup_dir = os.path.join(backup_base_dir, current_date)
    
    # Create a list to store information about backed up files
    backup_info = []

    # Build a set of existing MD5 hashes
    existing_hashes = build_existing_hash_list(backup_base_dir)

    for source_dir in source_dirs:
        for root, dirs, files in os.walk(source_dir):
                    
            # Exclude directories and their subdirectories based on the excluded_dirs list
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in excluded_dirs]

            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, source_dir)
                backup_file = os.path.join(backup_dir, relative_path)

                # Calculate the MD5 hash of the source file
                file_hash = calculate_hash(source_file)

                if file_hash not in existing_hashes:
                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    shutil.copy2(source_file, backup_file)
                    print(f"Backed up: {relative_path} to {backup_dir}")

                    # Add file information to the backup_info list
                    backup_info.append((source_file, backup_file, file_hash))

    
    # Create and save the backup database text file
    database_file = os.path.join(backup_base_dir, f"backup_database_{current_date}.txt")
    with open(database_file, 'w') as db:
        for source_file, backup_file, file_hash in backup_info:
            db.write(f"Source: {source_file}\n")
            db.write(f"Backup: {backup_file}\n")
            db.write(f"MD5 Hash: {file_hash}\n\n")

    print(f"Backup database saved to: {database_file}")

if __name__ == "__main__":
    incremental_backup(source_dirs, backup_base_dir)
