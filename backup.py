import os
import shutil
import hashlib
import datetime
import logging
from restore import list_all_backups
# Import the configuration
if str(os.name) == 'nt':
    from backup_config_windows import source_dirs, backup_base_dir, excluded_dirs
else:
    from backup_config import source_dirs, backup_base_dir, excluded_dirs

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

# Configure the logging
log_file = os.path.join(backup_base_dir, 'backup_log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Function to calculate the MD5 hash of a file including its path
def calculate_hash(file_path):
    hasher = hashlib.md5()
    # Include the file path in the hash
    hasher.update(file_path.encode('utf-8'))  
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

# Function to build a list of MD5 hashes from existing backup database files
def list_latest_hashes(backup_info):
    latest_hashes = set()  # Set to store hashes of the latest backup copy of each source file

    for source_location, backups in backup_info.items():
        if backups:
            latest_backup = backups[-1]  # Get the latest version (last entry) from the list of backups
            md5_hash = latest_backup['md5_hash']
            # Add the hash to the set
            latest_hashes.add(latest_backup['md5_hash'])

    return latest_hashes

# Function to perform an incremental backup
def incremental_backup(source_dirs, backup_base_dir, excluded_dirs):
    # Get the current date and time as a string with second-level resolution (e.g., "2023-09-15_12-34-56")
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")

    # Get info on previous backups
    old_backup_info, _ = list_all_backups(backup_base_dir)

    # Build a set of existing MD5 hashes
    latest_hashes = list_latest_hashes(old_backup_info)

    # Create a list to store information about backed up files
    backup_info = []

    for source_dir in source_dirs:
        for root, dirs, files in os.walk(source_dir):
            # Exclude directories and their subdirectories based on the excluded_dirs list
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in excluded_dirs]

            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, source_dir)

                # Calculate the MD5 hash of the source file
                file_hash = calculate_hash(source_file)
                # Output a '.' as a progress indicator
                print(".", end="", flush=True)  

                if file_hash not in latest_hashes:
                    # Build the backup directory structure with source directories as subdirectories
                    source_dir_name = os.path.basename(source_dir)
                    backup_dir = os.path.join(backup_base_dir, current_datetime, source_dir_name)
                    backup_file = os.path.join(backup_dir, relative_path)

                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    shutil.copy2(source_file, backup_file)
                    print(f"Backed up: {relative_path} to {backup_file}")

                    # Add file information to the backup_info list
                    backup_info.append((source_file, backup_file, file_hash))

    # Create and save the backup database text file
    database_file = os.path.join(backup_base_dir, f"backup_database_{current_datetime}.txt")
    with open(database_file, 'w') as db:
        for source_file, backup_file, file_hash in backup_info:
            db.write(f"Source: {source_file}\n")
            db.write(f"Backup: {backup_file}\n")
            db.write(f"MD5 Hash: {file_hash}\n\n")

    print(f"\nBackup database saved to: {database_file}")

    # Log the date and number of files included in the backup
    num_files_in_backup = len(backup_info)
    logging.info(f"Backup Date/Time: {current_datetime}, Number of Files: {num_files_in_backup}")

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    incremental_backup(source_dirs, backup_base_dir, excluded_dirs)

    end_time = datetime.datetime.now()
    run_time = (end_time - start_time).total_seconds()

    print(f"\nBackup completed in {run_time:.2f} seconds.")