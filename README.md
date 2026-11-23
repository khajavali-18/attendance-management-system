# AttendEase - Student Attendance Management System

A beginner-friendly attendance web application using HTML, CSS, JavaScript and Python Flask. The database is SQLite so it works immediately without installing or configuring MySQL.


## Features
- Demo admin login
- Add students (USN, name, department, semester)
- Mark attendance for a selected date
- Save/update daily attendance records
- Attendance reports and percentages
- Highlight students below 75%
- Print reports
- Responsive layout

## Requirements
- Python 3.9 or later
- Internet connection for Google Fonts (optional; system fonts work without it)

## Run on Windows (VS Code)
1. Extract the ZIP and open the `attendance_management` folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
4. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this once in the current terminal:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
   Then activate again.
5. Install Flask:
   ```powershell
   pip install -r requirements.txt
   ```
6. Start the application:
   ```powershell
   python app.py
   ```
7. Open the local address shown in the terminal, usually `http://127.0.0.1:5000`.


## Notes
- The database file `attendance.db` is automatically created the first time you run `app.py`.
- The demo login is hardcoded and not suitable for production. Change the secret key, add hashed user accounts, CSRF protection, and production server configuration before deployment.
