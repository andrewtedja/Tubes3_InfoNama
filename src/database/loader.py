import os
import mysql.connector
from dotenv import load_dotenv
from database.rsa import rsa_decrypt
from datetime import datetime
import time


def load_all_data():
    """
    Load all data in database (applicantprofile natural join applicationdetail)
    Decrypts all data
    Returns: List of JSON (decrypted_data)
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
    print("Decrypting loaded data...")

    start_time = time.time()
    decrypted_data = []
    cache = {}

    for idx, row in enumerate(rows):
        row_dict = dict(zip(columns, row))
        applicant_id = row_dict.get("applicant_id")

        if applicant_id in cache:
            cached = cache[applicant_id]
            row_dict.update({
                "first_name": cached["first_name"],
                "last_name": cached["last_name"],
                "address": cached["address"],
                "phone_number": cached["phone_number"],
                "date_of_birth": cached["date_of_birth"],
            })
        else:
            try:
                decrypted = {
                    "first_name": rsa_decrypt(row_dict["first_name"]),
                    "last_name": rsa_decrypt(row_dict["last_name"]),
                    "address": rsa_decrypt(row_dict["address"]),
                    "phone_number": rsa_decrypt(row_dict["phone_number"]),
                }
                dob_str = rsa_decrypt(row_dict["date_of_birth"])
                decrypted["date_of_birth"] = datetime.strptime(dob_str, "%Y-%m-%d").date()

                row_dict.update(decrypted)
                cache[applicant_id] = decrypted

            except Exception as e:
                print(f"[{idx}] ❌ Decrypt failed for applicant_id={applicant_id}: {e}")
        
        decrypted_data.append(row_dict)

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Decryption finished in {elapsed:.2f} seconds")

    conn.commit() 
    cursor.close()
    conn.close()

    return decrypted_data

if __name__ == "__main__":
    load_all_data()
