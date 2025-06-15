import os
import mysql.connector
from dotenv import load_dotenv
from database.rsa import rsa_encrypt

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

    cursor.execute("SELECT applicant_id, first_name, last_name, date_of_birth, address, phone_number FROM ApplicantProfile")
    rows = cursor.fetchall()

    for row in rows:
        applicant_id, first_name, last_name, dob, address, phone = row

        cursor.execute("""
            UPDATE ApplicantProfile
            SET first_name = %s,
                last_name = %s,
                date_of_birth = %s,
                address = %s,
                phone_number = %s
            WHERE applicant_id = %s
        """, (
            rsa_encrypt(first_name or ""),
            rsa_encrypt(last_name or ""),
            rsa_encrypt(dob or ""),
            rsa_encrypt(address or ""),
            rsa_encrypt(phone or ""),
            applicant_id
        ))

    conn.commit()
    print("✅ Database seeded and encrypted successfully.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed_data()
