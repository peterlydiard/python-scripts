import os
import datetime

# Function to list the latest backed up copies of files
def list_latest_backups(backup_base_dir):
    backup_info = {}  # Dictionary to store file information

    # Iterate through backup directories
    for root, dirs, files in os.walk(backup_base_dir):
        for file in files:
            if file.startswith("backup_database_") and file.endswith(".txt"):
                database_file = os.path.join(root, file)
                with open(database_file, 'r') as db:
                    lines = db.readlines()
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

                                # Get the actual modification time of the file
                                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(backup_file))

                                # Get the file size from the file attributes
                                try:
                                    file_size = os.path.getsize(backup_file)
                                except OSError:
                                    # Handle cases where file size cannot be determined
                                    file_size = 0

                                backup_info[backup_file] = {
                                    'source_location': source_location,
                                    'backup_file': backup_file,
                                    'mod_time': file_mod_time,
                                    'size': file_size,
                                }

                        i += 1

    return backup_info

# Function to print and save the backup information
def print_and_save_backup_info(backup_info, output_file):
    with open(output_file, 'w') as f:
        for file, info in backup_info.items():
            f.write(f"File: {file}\n")
            f.write(f"Source Location: {info['source_location']}\n")  # Source location first
            f.write(f"Backup Location: {info['backup_file']}\n")
            f.write(f"Modified Time: {info['mod_time']}\n")
            f.write(f"Size: {info['size']} bytes\n")
            f.write("\n")

    print("Latest Backups:")
    for file, info in backup_info.items():
        print(f"File: {file}")
        print(f"Source Location: {info['source_location']}")  # Source location first
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

    # Specify the full path to the output file within the backup base directory
    output_file = os.path.join(backup_base_dir, "backup_info.txt")

    # Check if the output file already exists and delete it if it does
    if os.path.exists(output_file):
        os.remove(output_file)

    backup_info = list_latest_backups(backup_base_dir)

    if not backup_info:
        print("No backup information found.")
    else:
        print_and_save_backup_info(backup_info, output_file)
