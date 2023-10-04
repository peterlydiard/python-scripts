import os
import logging

from backup import list_all_backups
# from restore_gui import create_window, make_backup_table, display_backup_table

# Import the configuration
if str(os.name) == 'nt':
    from backup_config_windows import backup_base_dir
else:
    from backup_config import backup_base_dir

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

# Check if backup directory exists and has necessary permissions

if not check_directory(backup_base_dir, write=True):
    print("Please check backup base directory path and write permissions.")
    logging.error("Error: Backup base directory path or write permissions are invalid.")
    exit(1)

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
        script_file.write('echo "Are you sure you want to restore files from backup? (Y/N)"\n')
        script_file.write('read choice\n')
        script_file.write('if [[ ! "$choice" =~ ^[Yy]$ ]]; then\n')
        script_file.write('    echo "Operation aborted."\n')
        script_file.write('    exit 1\n')
        script_file.write('fi\n')
        for source_location, backups in backup_info.items():
            latest_backup = backups[-1]  # Get the latest version (last entry) from the list of backups
            backup_file = latest_backup['backup_file']
            script_file.write(f'cp "{backup_file}" "{source_location}')
            script_file.write('|| {\n')
            script_file.write('    exit_code=$?\n')
            script_file.write(f'    echo "{source_location} restore failed with exit code: $exit_code"\n')
            script_file.write('}\n')
    print("Restore script 'restore_backup.sh' generated successfully.")


def generate_windows_restore_script(backup_info, batch_file_path):
    with open(batch_file_path, 'w') as batch_file:
        batch_file.write('REM Backup restore script\n\n') 
        batch_file.write('@echo off\n')
        batch_file.write('setlocal enabledelayedexpansion\n')
        batch_file.write('echo Are you sure you want to restore files from backup? (Y/N)\n')
        batch_file.write('set /p choice=\n')
        batch_file.write('if /i not "%choice%"=="Y" (\n')
        batch_file.write('    echo Operation aborted.\n')
        batch_file.write('    exit /b 1\n)\n')
        for source_location, backups in backup_info.items():
            latest_backup = backups[-1]  # Get the latest version (last entry) from the list of backups
            backup_file = latest_backup['backup_file']
            source_dir = os.path.dirname(source_location)
            batch_file.write(f'if not exist "{source_dir}" mkdir "{source_dir}"\n')
            batch_file.write(f'copy "{backup_file}" "{source_location}"\n')
            batch_file.write(f'if errorlevel 1 (\n')
            batch_file.write(f'    echo Restoring {source_location} failed with exit code: %errorlevel%\n)\n')
        batch_file.write('echo Files restored from backup.\n')
        batch_file.write('timeout /T 15\n')
    print("Restore script 'restore_backup.bat' generated successfully.")


if __name__ == "__main__":

    # Specify the full path to the output file within the backup base directory
    output_file = os.path.join(backup_base_dir, "backup_info.txt")

    # Check if the output file already exists and delete it if it does
    if os.path.exists(output_file):
        os.remove(output_file)

    # Get backup info and check file hashes
    backup_info, backup_times = list_all_backups(backup_base_dir, True)

    if not backup_info:
        print("No backup information found.")
    else:
        print_and_save_backup_info(backup_info, output_file)

    # Specify the full path to the script within the backup base directory
    if str(os.name) == 'nt':
        script_file_path = os.path.join(backup_base_dir, "restore_backup.bat")
        generate_windows_restore_script(backup_info, script_file_path)
    else:
        script_file_path = os.path.join(backup_base_dir, "restore_backup.sh")
        generate_restore_script(backup_info, script_file_path)
