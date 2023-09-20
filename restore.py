import os
import datetime

# Function to list the latest backed up copies of files
def list_latest_backups(backup_base_dir):
    backup_info = {}  # Dictionary to store file information

    # Iterate through backup directories
    for root, dirs, files in os.walk(backup_base_dir):
        for file in files:
            if not file.startswith("backup_database_") and not file.endswith(".txt"):
                backup_file = os.path.join(root, file)
                file_info = os.stat(backup_file)
                file_size = file_info.st_size
                file_mod_time = datetime.datetime.fromtimestamp(file_info.st_mtime)

                # Check if we already have a record for this file
                if file in backup_info:
                    # If this backup is more recent, update the record
                    if file_mod_time > backup_info[file]['mod_time']:
                        backup_info[file] = {
                            'backup_file': backup_file,
                            'mod_time': file_mod_time,
                            'size': file_size,
                        }
                else:
                    # Add a new record for this file
                    backup_info[file] = {
                        'backup_file': backup_file,
                        'mod_time': file_mod_time,
                        'size': file_size,
                    }

    return backup_info

# Function to print and save the backup information
def print_and_save_backup_info(backup_info, output_file):
    with open(output_file, 'w') as f:
        for file, info in backup_info.items():
            f.write(f"File: {file}\n")
            f.write(f"Backup Location: {info['backup_file']}\n")
            f.write(f"Modified Time: {info['mod_time']}\n")
            f.write(f"Size: {info['size']} bytes\n")
            f.write("\n")

    print("Latest Backups:")
    for file, info in backup_info.items():
        print(f"File: {file}")
        print(f"Backup Location: {info['backup_file']}")
        print(f"Modified Time: {info['mod_time']}")
        print(f"Size: {info['size']} bytes")
        print()

if __name__ == "__main__":
    try:
        from backup_config import backup_base_dir  # Import backup_base_dir from the configuration file
    except ImportError:
        print("Error: Unable to import backup_base_dir from backup_config.py.")
        exit(1)

    output_file = "backup_info.txt"  # Replace with the desired output file path

    backup_info = list_latest_backups(backup_base_dir)

    if not backup_info:
        print("No backup information found.")
    else:
        print_and_save_backup_info(backup_info, output_file)
