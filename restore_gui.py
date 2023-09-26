from guizero import App, Box, Text
app = 0
table_box = 0

def create_window():
    global app, table_box
    # Create an application
    app = App("Backup Info Table", width=600, height=400)

    # Create a Box widget to hold the table-like structure
    table_box = Box(app, layout="grid")

# Function to make the backup table - one row per source file
def make_backup_table(backup_info, backup_times):
    table = [] # List for function output

    # Generate reformatted column headings
    row_data = ["Source File"]
    for time_str in backup_times:
        # Stack the date and time (e.g., "2023-09-18_09h44m37s" to "2023-09-18\n09h44m37s")
        formatted_time = time_str.replace("_", "\n")
        row_data.append(formatted_time)
    table.append(row_data)

    # Generate the table rows, with one source file per row
    for source_location, backups in backup_info.items():
        row_data = [source_location]
        # Iterate through the table columns
        for _, time_str in enumerate(backup_times, start=1):
            cell_data = ""
            for _, backup in enumerate(backups): # Get info on each backup file
                backup_file = backup['backup_file']
                if time_str in backup_file:
                    cell_data = "1" if backup['hash_match'] else "?" # backup file found
                    break
            row_data.append(cell_data)

        table.append(row_data)

    return table

# Function to display the backup table
def display_backup_table(backup_table):
    global app, table_box
    if backup_table == []:
        return # nothing to display

    num_rows = len(backup_table)
    num_cols = len(backup_table[0])
    row = 0

    while row < num_rows:
        if row > 10:
            break # Display only the first 10 files
        col = 0
        while col < num_cols:
            # Left-justify the text in the first column
            justify = "left" if col == 0 else "right"
            text = backup_table[row][col]
            Text(table_box, text, grid=[col, row+1], align=justify)
            col += 1
        row += 1

    # Display the guizero application
    app.display()