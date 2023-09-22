import os
import datetime
import hashlib
from guizero import App, Box, Text, PushButton

# Create an application
app = App("Backup Info Table", width=600, height=400)

# Create a Box widget to hold the table-like structure
table_box = Box(app, layout="grid")

# Function to list the latest backed up copies of files
def list_latest_backups(backup_base_dir):
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

                                # Get the actual modification time of the file
                                file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(backup_file))

                                # Get the file size from the file attributes
                                try:
                                    file_size = os.path.getsize(backup_file)
                                except OSError:
                                    # Handle cases where file size cannot be determined
                                    file_size = 0
                                    
                                # Calculate the MD5 hash of the backup file using the source file path
                                calculated_md5 = calculate_hash(source_location, backup_file)

                                # Check if the calculated MD5 matches the saved MD5 from the database
                                if 'MD5 Hash' in lines[i + 1]:
                                    saved_md5 = lines[i + 1].strip().split(": ")[1]
                                    hash_match = calculated_md5 == saved_md5
                                else:
                                    hash_match = False

                                backup_info[backup_file] = {
                                    'source_location': source_location,
                                    'backup_file': backup_file,
                                    'mod_time': file_mod_time,
                                    'size': file_size,
                                    'hash_match': hash_match
                                }

                        i += 1

    return backup_info, backup_times

# Function to calculate the MD5 hash of a file using the source file path
def calculate_hash(source_file_path, backup_file_path):
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

# Function to print and save the backup information
def print_and_save_backup_info(backup_info, output_file):
    with open(output_file, 'w') as f:
        for file, info in backup_info.items():
            f.write(f"File: {file}\n")
            f.write(f"Source Location: {info['source_location']}\n")  # Source location first
            f.write(f"Backup Location: {info['backup_file']}\n")
            f.write(f"Modified Time: {info['mod_time']}\n")
            f.write(f"Size: {info['size']} bytes\n")
            f.write(f"Hash Match: {info['hash_match']}\n")
            f.write("\n")

    print("Latest Backups:")
    for file, info in backup_info.items():
        print(f"File: {file}")
        print(f"Source Location: {info['source_location']}")  # Source location first
        print(f"Backup Location: {info['backup_file']}")
        print(f"Modified Time: {info['mod_time']}")
        print(f"Size: {info['size']} bytes")
        print(f"Hash Match: {info['hash_match']}")
        print()

# Function to display the backup table
def display_backup_table(backup_info, backup_times):
    row = 1  # Start from the second row

    # Generate reformatted column headings
    col_headings = ["Source File"]
    for time_str in backup_times:
        # Reformat the date and time (e.g., "2023-09-18_09-44-37" to "2023-09-18\n09:44:37")
        formatted_time = time_str.replace("_", "\n")
        col_headings.append(formatted_time)

    # Display column headings
    for col, heading in enumerate(col_headings):
        # Left-justify the text in the first column
        justify = "left" if col == 0 else "right"
        Text(table_box, text=heading, grid=[col, 0], align=justify)

    for source_file, info in backup_info.items():
        if row > 10:
            break  # Display only the first 10 files
        # Left-justify the text in the first column
        Text(table_box, text=info['source_location'], grid=[0, row], align="left")
        
        # Add "1" to indicate backup presence based on info['hash_match'] for each backup
        # for col, time_str in enumerate(backup_times, start=1):
        #    if info['backup_file'] in backup_times[time_str]:
        #        Text(table_box, text="1" if info['hash_match'] else "", grid=[col, row], align="right")

        row += 1

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

    backup_info, backup_times = list_latest_backups(backup_base_dir)

    if not backup_info:
        print("No backup information found.")
    else:
        print_and_save_backup_info(backup_info, output_file)

    # Call the function to display the backup table
    display_backup_table(backup_info, backup_times)

    # Display the application
    app.display()
