import os
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
log_file = os.path.join(backup_base_dir, 'scratch_log.txt')
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

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    home_dir = common_parent_directory(source_dirs[0], backup_base_dir)
    print(f"Home directory = {home_dir}")

    end_time = datetime.datetime.now()
    run_time = (end_time - start_time).total_seconds()

    print(f"\nScratch completed in {run_time:.2f} seconds.")