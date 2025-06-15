import os 
import re 
import random 
from faker import Faker 
import mysql.connector 
from dotenv import load_dotenv 
 
fake = Faker("id_ID") 
 
def seed_data(data_dir='data', limit_per_role=20, max_cvs_per_applicant=5): 
    load_dotenv() 
 
    conn = mysql.connector.connect( 
        host="localhost", 
        user=os.getenv("MYSQL_USER"), 
        password=os.getenv("MYSQL_PASSWORD"), 
        database="ats" 
    ) 
    cursor = conn.cursor() 
 
    # Collect all PDFs from all roles
    all_cvs = []
    for role in os.listdir(data_dir): 
        role_path = os.path.join(data_dir, role) 
        if not os.path.isdir(role_path): 
            continue 
 
        pdf_files = [os.path.join(role_path, f) for f in os.listdir(role_path) if f.lower().endswith(".pdf")] 
        pdf_files.sort()
        pdf_files = pdf_files[:limit_per_role] 
        
        for pdf_file in pdf_files:
            all_cvs.append({'role': role, 'cv_path': pdf_file})
    
    total_cvs = len(all_cvs)
    if total_cvs == 0:
        print("No PDF files found!")
        return
    
    # Shuffle CVs
    random.shuffle(all_cvs)
    
    # Random number of applicants
    applicant_ratio = random.uniform(0.3, 0.8)
    num_applicants = max(1, int(total_cvs * applicant_ratio))
    
    print(f"Create {num_applicants} applicants for {total_cvs} CVs")
    
    # Create applicants and distribute CVs
    applicant_ids = []
    cv_assignments = []  # Tuples: (applicant_index, cv_data)
    
    # Create all applicants
    for i in range(num_applicants):
        first_name = fake.first_name() 
        last_name = fake.last_name() 
        dob = fake.date_of_birth(minimum_age=20, maximum_age=50).strftime("%Y-%m-%d") 
        address = fake.address().replace("\n", ", ") 
        raw_phone = fake.phone_number() 
        phone = re.sub(r'\D', '', raw_phone)[:20] 
 
        cursor.execute(""" 
            INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) 
            VALUES (%s, %s, %s, %s, %s) 
        """, (first_name, last_name, dob, address, phone)) 
 
        applicant_ids.append(cursor.lastrowid)
    
    # Distribute CVs
    cv_index = 0
    # At least 1 CV / applicant
    for applicant_idx in range(num_applicants):
        if cv_index < total_cvs:
            cv_assignments.append((applicant_idx, all_cvs[cv_index]))
            cv_index += 1
    
    # Distribute remaining CVs randomly
    while cv_index < total_cvs:
        applicant_idx = random.randint(0, num_applicants - 1)
        
        # Check too many CVs
        current_cv_count = sum(1 for a_idx, _ in cv_assignments if a_idx == applicant_idx)
        if current_cv_count < max_cvs_per_applicant:
            cv_assignments.append((applicant_idx, all_cvs[cv_index]))
            cv_index += 1
        else:
            # Find fewer CVs
            applicant_cv_counts = {}
            for a_idx, _ in cv_assignments:
                applicant_cv_counts[a_idx] = applicant_cv_counts.get(a_idx, 0) + 1
            
            # Find applicant with minimum CVs
            min_cvs = min(applicant_cv_counts.values())
            candidates = [a_idx for a_idx in range(num_applicants) 
                         if applicant_cv_counts.get(a_idx, 0) == min_cvs]
            
            selected_applicant = random.choice(candidates)
            cv_assignments.append((selected_applicant, all_cvs[cv_index]))
            cv_index += 1
    
    # Insert application details
    for applicant_idx, cv_data in cv_assignments:
        applicant_id = applicant_ids[applicant_idx]
        
        cursor.execute(""" 
            INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) 
            VALUES (%s, %s, %s) 
        """, (applicant_id, cv_data['role'], cv_data['cv_path']))
    
    conn.commit() 
    cursor.close() 
    conn.close() 
    
    # Stats
    applicant_cv_counts = {}
    for applicant_idx, _ in cv_assignments:
        applicant_cv_counts[applicant_idx] = applicant_cv_counts.get(applicant_idx, 0) + 1
    
    min_cvs = min(applicant_cv_counts.values())
    max_cvs = max(applicant_cv_counts.values())
    avg_cvs = len(cv_assignments) / len(applicant_ids)
    
    print(f"Seeding completed successfully!")
    print(f"Created {len(applicant_ids)} applicants")
    print(f"Assigned {len(cv_assignments)} CV applications")
    print(f"CVs per applicant - Min: {min_cvs}, Max: {max_cvs}, Avg: {avg_cvs:.1f}")
    print(f"All {total_cvs} CVs have been assigned to applicants")
 
if __name__ == "__main__": 
    seed_data()