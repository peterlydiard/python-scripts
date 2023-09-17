import os
import shutil
import hashlib
import datetime
import logging
from backup_config import source_dirs, backup_base_dir, excluded_dirs  # Import the configuration

# Configure the logging
log_file = os.path.join(backup_base_dir, 'backup_log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
                        file_key = lines[i - 2].strip()[8:]  # Extract the file key from the source line
                        existing_hashes.add(file_key)
    return existing_hashes

# Function to check if a directory path exists and has necessary permissions
def check_directory(path, write=False):
    if not os.path.exists(path):
        error_msg = f"Error: Directory does not exist: {path}"
        print(error_msg)
        logging.error(error_msg)
        return False
    if not os.access(path, os.R_OK):
        error_msg = f"Error: Insufficient permissions to read directory: {path}"
        print(error_msg)
        logging.error(error_msg)
        return False
    if write and not os.access(path, os.W_OK):
        error_msg = f"Error: Insufficient permissions to write to directory: {path}"
        print(error_msg)
        logging.error(error_msg)
        return False
    return True

# Check if source and backup directories exist and have necessary permissions
if not all(check_directory(source_dir) for source_dir in source_dirs):
    print("Please check source directory paths and permissions.")
    logging.error("Error: Source directory paths or permissions are invalid.")
    exit(1)

if not check_directory(backup_base_dir, write=True):
    print("Please check backup base directory path and write permissions.")
    logging.error("Error: Backup base directory path or write permissions are invalid.")
    exit(1)

# Function to perform an incremental backup
def incremental_backup(source_dirs, backup_base_dir, excluded_dirs):
    # Get the current date as a string (e.g., "2023-09-15")
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    # Create a list to store information about backed up files
    backup_info = []

    # Build a set of existing file keys
    existing_file_keys = build_existing_hash_list(backup_base_dir)

    for source_dir in source_dirs:
        for root, dirs, files in os.walk(source_dir):
            # Exclude directories and their subdirectories based on the excluded_dirs list
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in excluded_dirs]

            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, source_dir)

                # Calculate the MD5 hash of the source file
                file_hash = calculate_hash(source_file)

                # Construct a unique key for each file based on source path, relative path, and hash
                file_key = f"{source_dir}|{relative_path}|{file_hash}"

                if file_key not in existing_file_keys:
                    # Build the backup directory structure with source directories as subdirectories
                    source_dir_name = os.path.basename(source_dir)
                    backup_dir = os.path.join(backup_base_dir, current_date, source_dir_name)
                    backup_file = os.path.join(backup_dir, relative_path)

                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    shutil.copy2(source_file, backup_file)
                    print(f"Backed up: {relative_path} to {backup_file}")

                    # Add file information to the backup_info list
                    backup_info.append((source_file, backup_file, file_key))

    # Create and save the backup database text file
    database_file = os.path.join(backup_base_dir, f"backup_database_{current_date}.txt")
    with open(database_file, 'w') as db:
        for source_file, backup_file, file_key in backup_info:
            db.write(f"Source: {source_file}\n")
            db.write(f"Backup: {backup_file}\n")
            db.write(f"File Key: {file_key}\n\n")

    print(f"Backup database saved to: {database_file}")

    # Log the date and number of files included in the backup
    num_files_in_backup = len(backup_info)
    logging.info(f"Backup Date: {current_date}, Number of Files: {num_files_in_backup}")

if __name__ == "__main__":
    incremental_backup(source_dirs, backup_base_dir, excluded_dirs)
