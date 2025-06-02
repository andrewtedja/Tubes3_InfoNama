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

## How To Run
Run the program
```bash
uv run main.py
```