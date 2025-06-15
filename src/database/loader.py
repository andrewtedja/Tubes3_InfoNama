import os
import mysql.connector
from dotenv import load_dotenv


def load_all_data():
    """
    Load all data in database (applicantprofile natural join applicationdetail)
    
    Returns: List of JSON (data)
    """
    load_dotenv()

    conn = mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database="ats"
    )
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM applicantprofile NATURAL JOIN applicationdetail
    """)

    rows = cursor.fetchall()
    columns = cursor.column_names
    data = [dict(zip(columns, row)) for row in rows]


    conn.commit() 
    cursor.close()
    conn.close()

    # print(data)

    return data

if __name__ == "__main__":
    load_all_data()
