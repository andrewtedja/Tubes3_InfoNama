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
source .venv/Scripts/activate

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

# 2. Run create_tables.py
uv run src/database/create_tables.py

# 3. Run seeder.py
uv run src/database/seeder.py
```

## How To Run
Run the program
```bash
uv run main.py
```