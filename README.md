# Tubes3_InfoNama

## How To Run
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

Run the program
```bash
uv run main.py
```