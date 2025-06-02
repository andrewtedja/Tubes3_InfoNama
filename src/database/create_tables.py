import os
import mysql.connector
from dotenv import load_dotenv

def create_tables():
    load_dotenv()

    # Create database if not exist
    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS ATS;")
    print("Database 'ATS' ensured.")
    cursor.close()
    conn.close()

    # Connection with ATS database
    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database="ats"
    )
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS ApplicationDetail;")
    cursor.execute("DROP TABLE IF EXISTS ApplicantProfile;")
    print("Existing tables dropped.")

    # Make tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ApplicantProfile (
        applicant_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50) DEFAULT NULL,
        last_name VARCHAR(50) DEFAULT NULL,
        date_of_birth DATE DEFAULT NULL,
        address VARCHAR(255) DEFAULT NULL,
        phone_number VARCHAR(20) DEFAULT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ApplicationDetail (
        detail_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        applicant_id INT NOT NULL,
        application_role VARCHAR(100) DEFAULT NULL,
        cv_path TEXT,
        FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)
    );
    """)

    print("Tables created successfully.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
