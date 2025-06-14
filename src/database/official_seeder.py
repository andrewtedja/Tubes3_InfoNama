import os
import re 
import mysql.connector
from dotenv import load_dotenv


def seed_data():
    load_dotenv()

    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database="ats"
    )
    cursor = conn.cursor()

    with open("data/tubes3_seeding.sql", "r", encoding="utf-8") as f:
        sql_commands = f.read()

    # Split commands
    for command in sql_commands.split(";"):
        command = command.strip()
        if command:
            try:
                cursor.execute(command)
            except mysql.connector.Error as err:
                print(f"Failed executing: {command}\nError: {err}")

    conn.commit() 
    cursor.close() 
    conn.close()

if __name__ == "__main__":
    seed_data()
