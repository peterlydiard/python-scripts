import os

from backup import list_all_backups
from restore_gui import create_window, make_backup_table, display_backup_table


# Function to print and save the backup information
def print_and_save_backup_info(backup_info, output_file):
    with open(output_file, 'w') as f:
        for source_location, backups in backup_info.items():
            f.write(f"Source Location: {source_location}\n")
            for i, backup in enumerate(backups):
                f.write(f"Backup {i + 1} Location: {backup['backup_file']}\n")
                f.write(f"Modified Time: {backup['mod_time']}\n")
                f.write(f"Size: {backup['size']} bytes\n")
                f.write(f"MD5 Hash: {backup['md5_hash']}\n")
                f.write(f"Hash Match: {backup['hash_match']}\n")
            f.write("\n")

    print("All Backups:")
    for source_location, backups in backup_info.items():
        print(f"Source Location: {source_location}")
        for i, backup in enumerate(backups):
            print(f"Backup {i + 1} Location: {backup['backup_file']}")
            print(f"Modified Time: {backup['mod_time']}")
            print(f"Size: {backup['size']} bytes")
            print(f"MD5 Hash: {backup['md5_hash']}\n")
            print(f"Hash Match: {backup['hash_match']}")
        print()


def generate_restore_script(backup_info, script_file_path):
    with open(script_file_path, 'w') as script_file:
        script_file.write('#!/bin/bash\n\n')
        for source_location, backups in backup_info.items():
            latest_backup = backups[-1]  # Get the latest version (last entry) from the list of backups
            backup_file = latest_backup['backup_file']
            script_file.write(f'cp "{backup_file}" "{source_location}"\n')
    print("Restore script 'restore_backup.sh' generated successfully.")


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

    backup_info, backup_times = list_all_backups(backup_base_dir)

    if not backup_info:
        print("No backup information found.")
    else:
        print_and_save_backup_info(backup_info, output_file)

    # Specify the full path to the script within the backup base directory
    script_file_path = os.path.join(backup_base_dir, "restore_backup.sh")
    generate_restore_script(backup_info, script_file_path)

    # create_window()

    # Call the functions to make and display the backup table
    # table = make_backup_table(backup_info, backup_times)

    # display_backup_table(table)