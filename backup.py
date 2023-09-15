# ------------------------------
# Imports
# ------------------------------
import os
import shutil
import hashlib
import datetime

# Source and destination directories
source_dir = "/home/peter/Pictures"
backup_base_dir = '/home/peter/History'

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

# Function to perform an incremental backup
def incremental_backup(source_dir, backup_base_dir):
    # Get the current date as a string (e.g., "2023-09-15")
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # Create a subdirectory with the current date in the backup base directory
    backup_dir = os.path.join(backup_base_dir, current_date)
    
    file_system = list(os.walk(source_dir))
    if file_system == []:
        print("No file system at ", source_dir)
        return
    
    # Create a list to store information about backed up files
    backup_info = []

    for root, _, files in file_system:
        for file in files:
            source_file = os.path.join(root, file)
            relative_path = os.path.relpath(source_file, source_dir)
            backup_file = os.path.join(backup_dir, relative_path)

            if not os.path.exists(backup_file) or calculate_hash(source_file) != calculate_hash(backup_file):
                os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                shutil.copy2(source_file, backup_file)
                print(f"Backed up: {relative_path} to {backup_dir}")

                # Calculate the MD5 hash of the source file
                file_hash = calculate_hash(source_file)

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
    incremental_backup(source_dir, backup_base_dir)
