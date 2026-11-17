# Jr. Ramanuja

A kid-friendly mathematics practice web application built with **Python, Flask, SQLite, HTML, CSS and JavaScript**.

## Features

- User registration and login
- Addition, subtraction, multiplication and division practice
- Random practice mode
- Configurable number range and quiz length
- Score and progress tracking
- SQLite database created automatically on first run
- Passwords stored as secure hashes (not plain text)

## Tech stack

- Python 3.9+
- Flask
- SQLite
- HTML, CSS and JavaScript

## Project structure

```text
Jr_Ramanuja/
├── app.py
├── create_db.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── database.db          # created automatically; not committed to Git
├── static/
│   └── logo.png
└── templates/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── quiz.html
    └── progress.html
```

## Run locally

1. Install Python 3.9 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   source venv/bin/activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   python app.py
   ```

   The SQLite database and required tables are created automatically when the app starts.

7. Open this address in your browser:

   ```text
   http://127.0.0.1:5000
   ```

8. Register a new account and start practising.

## Database and privacy

The repository intentionally does **not** include a database file or any real user records. Each person gets a fresh local `database.db` when they run the application. The database is excluded from Git by `.gitignore`.

Passwords are hashed before being stored. Do not commit `.env` files, secret keys, real user data, or local database files.

For deployment, set a strong random `SECRET_KEY` environment variable. The app generates a temporary key automatically for local demonstration if one is not configured.

## Notes

- The app is intended as a learning / academic project.
- The division quiz creates valid integer division questions within the selected number range.
- Google Fonts are loaded from the internet; the app still runs without them, using the browser's fallback font.

## License

Add a license file if you want others to reuse, modify, or distribute this project. Until then, all rights are reserved by the author.
