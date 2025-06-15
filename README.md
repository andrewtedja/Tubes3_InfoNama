# Tubes3_InfoNama

## How To Setup

If uv has not been installed

```bash
pipx install uv
uv --version
uv pip install .
```

To connect with venv

```bash
uv venv # If venv has not been created

# For Windows
.venv/Scripts/activate

# For UNIX
source .venv/bin/activate
```

Install dependencies

```bash
uv pip install -r requirements.txt
```

Create Database

```bash
# 1. Create new .env file in root with this content:
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# 2. Generate your public and private key:
uv run src/database/rsa.py

# You can use the provided .env.example file as a template:
cp .env.example .env

# 3. Create database and tables if hasn't been created
uv run src/database/create_tables.py

# 4. Seed the database (creates tables + inserts + encryption)
uv run src/database/official_seeder.py

# or use the random seeder:
uv run src/database/seeder.py
```

## How To Run

Run the program

```bash
uv run src/main.py
```
