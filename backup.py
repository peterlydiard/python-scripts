import os
import shutil
import hashlib
import datetime
import logging
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

def common_parent_directory(path1, path2):
    """
    Calculate the path of the lowest level directory that contains the two input paths.
    Args:
        path1 (str): First file path.
        path2 (str): Second file path.
    Returns:
        str: Path of the common parent directory.
    """
    # Get the absolute paths to handle relative paths correctly
    abs_path1 = os.path.abspath(path1)
    abs_path2 = os.path.abspath(path2)

    # Split the paths into directories
    dir_parts1 = abs_path1.split(os.path.sep)
    dir_parts2 = abs_path2.split(os.path.sep)

    # Find the common parent directory
    common_dir = []
    for dir1, dir2 in zip(dir_parts1, dir_parts2):
        if dir1 == dir2:
            common_dir.append(dir1)
        else:
            break

    # If there is no common parent directory, return the immediate parent of the first directory
    if not common_dir:
        return os.path.dirname(abs_path1)
    
    # Join the common directory parts to get the full path
    common_path = os.path.join(*common_dir)

    # Add initial '/' for Linux paths
    if os.name == 'posix':
        common_path = os.path.sep + os.path.join(*common_dir)

    # For Windows, handle drive letter
    if os.name == 'nt':
        common_path = common_path.split(':\\')[0] + ':\\' + common_path.split(':\\')[1]

    return common_path


# Function to list all the backed up copies of files
def list_all_backups(backup_base_dir, check_hash):
    backup_info = {}  # Dictionary to store file information
    backup_times = []  # List to store unique dates and times of backups

    # Iterate through backup directories
    for root, dirs, files in os.walk(backup_base_dir):
        for file in files:
            if file.startswith("backup_database_") and file.endswith(".txt"):
                database_file = os.path.join(root, file)
                with open(database_file, 'r') as db:
                    lines = db.readlines()

                    # Extract date and time information from the backup database file name
                    date_time = os.path.splitext(file)[0].split("database_")[1]  # Assuming the format is yyyy-mm-dd_hh-mm-ss
                    # Add the unique date and time to the list
                    if date_time not in backup_times:
                        backup_times.append(date_time)

                    i = 0
                    while i < len(lines):
                        # Check if the line starts with "Source: " and has at least 10 characters
                        if lines[i].startswith("Source: ") and len(lines[i]) >= 10:
                            source_location = lines[i].strip().split(": ")[1]
                            i += 1

                            # Check if there are enough lines in the file
                            if i >= len(lines):
                                break

                            # Check if the line starts with "Backup: " and has at least 10 characters
                            if lines[i].startswith("Backup: ") and len(lines[i]) >= 10:
                                backup_file = lines[i].strip().split(": ")[1]

                                # Get the actual modification time of the backup file
                                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(backup_file))

                                # Get the file size from the file attributes
                                try:
                                    file_size = os.path.getsize(backup_file)
                                except OSError:
                                    # Handle cases where file size cannot be determined
                                    file_size = 0
                                    
                                # Calculate the MD5 hash of the backup file using the source file path
                                if check_hash:
                                    calculated_md5 = calculate_backup_hash(source_location, backup_file)
                                else:
                                    calculated_md5 = 0

                                # Check if the calculated MD5 matches the saved MD5 from the database
                                if 'MD5 Hash' in lines[i + 1]:
                                    saved_md5 = lines[i + 1].strip().split(": ")[1]
                                    hash_match = calculated_md5 == saved_md5
                                else:
                                    hash_match = False

                                # Check if the source_location is already a key in backup_info
                                if source_location not in backup_info:
                                    backup_info[source_location] = []

                                # Append the backup file information to the list associated with source_location
                                backup_info[source_location].append({
                                    'backup_file': backup_file,
                                    'mod_time': file_mod_time,
                                    'size': file_size,
                                    'md5_hash': saved_md5,
                                    'hash_match': hash_match
                                })

                        i += 1

    return backup_info, backup_times

# Function to calculate the MD5 hash of a backup file using the source file path
def calculate_backup_hash(source_file_path, backup_file_path):
    hasher = hashlib.md5()
    # Include the file path in the hash
    hasher.update(source_file_path.encode('utf-8'))  
    with open(backup_file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

# Function to calculate the MD5 hash of a source file including its path
def calculate_source_hash(file_path):
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
            latest_hashes.add(md5_hash)

    return latest_hashes

# Function to perform an incremental backup
def incremental_backup(source_dirs, backup_base_dir, excluded_dirs):
    # Get the current date and time as a string with second-level resolution (e.g., "2023-09-15_12-34-56")
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")

    # Get info on previous backups without checking file hashes
    old_backup_info, _ = list_all_backups(backup_base_dir, False)

    # Build a set of existing MD5 hashes
    latest_hashes = list_latest_hashes(old_backup_info)

    # Create a list to store information about backed up files
    backup_info = []

    for source_dir in source_dirs:
        home_dir = common_parent_directory(source_dir, backup_base_dir)

        for root, dirs, files in os.walk(source_dir):
            # Exclude directories and their subdirectories based on the excluded_dirs list
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in excluded_dirs]

            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, home_dir)

                # Calculate the MD5 hash of the source file
                file_hash = calculate_source_hash(source_file)
                # Output a '.' as a progress indicator
                print(".", end="", flush=True)  

                if file_hash not in latest_hashes:
                    # Build the backup directory structure with source directories as subdirectories
                    backup_dir = os.path.join(backup_base_dir, current_datetime)
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