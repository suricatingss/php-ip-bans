try:
    import sqlite3
    import re
except ModuleNotFoundError:
    print("You don't have SQLite!")
    print("If you are using Debian-related linux, run\n >> sudo apt install libsqlite3-dev python3-dev python3-full -y")
    

def time_to_seconds(time_str):
    """Convert a time string to seconds."""
    units:dict = {
        's': 1,          # Seconds
        'm': 60,         # Minutes
        'h': 3600,       # Hours
        'd': 86400,      # Days
        'w': 604800      # Weeks
    }
    match = re.match(r"(\d+)([smhdw])$", time_str)
    if not match:
        raise ValueError("Invalid time format. Use a number followed by a unit (s, m, h, d, w).")
    
    value, unit = match.groups()
    return int(value) * units[unit]


def prompt_import_or_setup(table_name):
    """Ask the user if they want to import data or set up the table."""
    while True:
        choice = input(f"Do you want to import an existing {table_name} table? (yes/no): ").strip().lower()
        if choice in ['yes', 'no']:
            return choice == 'yes'
        print("Invalid input. Please enter 'yes' or 'no'.")


def setup_database():
    """Create the database schema."""
    print("Welcome! This script will guide you in setting up the database for IP bans.")

    db_name = "bansystem.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Users Table
    if not prompt_import_or_setup("users"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            IP VARCHAR PRIMARY KEY,
            strikes INT DEFAULT 0,
            ban_permanent BOOLEAN DEFAULT 0,
            ban_time TIMESTAMP NULL,
            expiry TIMESTAMP NULL
        );
        """)
        print("Users table created.")

    # Strikes Table
    if not prompt_import_or_setup("strikes"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS strikes (
            strike_num INT PRIMARY KEY,
            timeout INT NOT NULL
        );
        """)
        print("Strikes table created.")

    # Settings Table
    if not prompt_import_or_setup("settings"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            name VARCHAR PRIMARY KEY,
            key VARCHAR NOT NULL
        );
        """)
        print("Settings table created.")

    conn.commit()

    return conn, cursor


def add_strike_rules(cursor):
    """Add strike rules to the database."""
    print("\nLet's configure the strike rules.")
    print("Example input:")
    print("Enter number of attempts and its ban time (<strike> <timeout>)")
    print("For timeout, use number and unit (e.g., 30s, 1h, 6h, 1d, 1w)")
    print("Enter '<strike> permanent' for a permanent ban.")
    print("Enter 'done' when you are finished.\n")

    strike_rules = []
    while True:
        rule = input("Enter a strike rule: ").strip().lower()
        if rule == 'done': break

        try:
            if "permanent" in rule:
                strike_num = int(rule.split()[0])
                timeout = -1
            else:
                strike_num, timeout_str = rule.split()
                strike_num = int(strike_num)
                timeout = time_to_seconds(timeout_str)

            strike_rules.append((strike_num, timeout))
        except Exception as e:
            print(f"Invalid input: {e}")
            continue

    # Insert strike rules into the database
    cursor.executemany("INSERT OR IGNORE INTO strikes (strike, timeout) VALUES (?, ?);", strike_rules)
    print("Strike rules added successfully.")


def add_settings(cursor):
    """Add default settings to the database."""
    print("\nConfiguring default settings.")

    expiry_time = input("Enter default expiry time (e.g., 1h, 1d, 1w) or 'None' for all records to last forever\n(The expiry date only removes the record if the user is NOT banned) : ").strip().lower()
    try:
        expiry_seconds = time_to_seconds(expiry_time)
        cursor.execute("INSERT OR REPLACE INTO settings (name, key) VALUES (?, ?);", ("default_expiry", str(expiry_seconds)))
        print("Default expiry time added successfully.")
    except ValueError as e:
        print(f"Invalid expiry time: {e}")
        print("Skipping default expiry time.")


def import_existing_data(cursor, table_name):
    """Prompt user to import existing data into a specific table."""
    file_path = input(f"Enter the file path for {table_name} data (CSV format): ").strip()
    try:
        with open(file_path, 'r') as file:
            rows = [line.strip().split(',') for line in file.readlines()]

        if table_name == "users":
            cursor.executemany("INSERT OR IGNORE INTO users (ip, strikes, ban_permanent, ban_time, expiry) VALUES (?, ?, ?, ?, ?);", rows)
        elif table_name == "strikes":
            cursor.executemany("INSERT OR IGNORE INTO strikes (strike_num, timeout) VALUES (?, ?);", rows)
        elif table_name == "settings":
            cursor.executemany("INSERT OR IGNORE INTO settings (name, key) VALUES (?, ?);", rows)

        print(f"Data imported successfully into the {table_name} table.")
    except Exception as e:
        print(f"Failed to import data: {e}")


if __name__ == "__main__":
    conn, cursor = setup_database()

    # Prompt to configure strike rules
    if not prompt_import_or_setup("strikes"):
        add_strike_rules(cursor)

    # Prompt to configure default settings
    if not prompt_import_or_setup("settings"):
        add_settings(cursor)

    conn.commit()
    conn.close()

    print("\nDatabase setup completed successfully.")
