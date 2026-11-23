from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'replace-this-secret-key-before-deployment'
DB_PATH = Path(__file__).with_name('attendance.db')


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL DEFAULT 'CSE',
            semester INTEGER NOT NULL DEFAULT 1
        )''')
        con.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
            UNIQUE(student_id, attendance_date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )''')


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper


@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        # Demo login credentials. Change before using outside a classroom demo.
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash('Incorrect username or password.', 'error')
    return render_template('login.html')



@app.route('/dashboard')
@login_required
def dashboard():
    selected_date = request.args.get('date', date.today().isoformat())
    with db() as con:
        total = con.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        present = con.execute("SELECT COUNT(*) FROM attendance WHERE attendance_date=? AND status='Present'", (selected_date,)).fetchone()[0]
        absent = con.execute("SELECT COUNT(*) FROM attendance WHERE attendance_date=? AND status='Absent'", (selected_date,)).fetchone()[0]
        marked = present + absent
        students = con.execute('''SELECT s.*, a.status FROM students s LEFT JOIN attendance a
            ON s.id=a.student_id AND a.attendance_date=? ORDER BY s.usn''', (selected_date,)).fetchall()
    return render_template('dashboard.html', total=total, present=present, absent=absent, marked=marked,
                         students=students, selected_date=selected_date)


@app.route('/students/add', methods=['POST'])
@login_required
def add_student():
    usn = request.form.get('usn', '').strip().upper()
    name = request.form.get('name', '').strip()
    department = request.form.get('department', 'CSE').strip() or 'CSE'
    try:
        semester = int(request.form.get('semester', 1))
        if not (1 <= semester <= 8):
            raise ValueError
        if not usn or not name:
            flash('Please fill in USN and student name.', 'error')
        else:
            with db() as con:
                con.execute('INSERT INTO students (usn, name, department, semester) VALUES (?, ?, ?, ?)',
                          (usn, name, department, semester))
            flash(f'Student {name} added successfully.', 'success')
    except sqlite3.IntegrityError:
        flash('That USN is already registered.', 'error')
    except ValueError:
        flash('Semester must be a number between 1 and 8.', 'error')
    return redirect(url_for('dashboard'))


@app.route('/attendance/save', methods=['POST'])
@login_required
def save_attendance():
    attendance_date = request.form.get('attendance_date', date.today().isoformat())
    with db() as con:
        students = con.execute('SELECT id FROM students').fetchall()
        for student in students:
            status = request.form.get(f'status_{student["id"]}', 'Absent')
            if status not in ('Present', 'Absent'):
                status = 'Absent'
            con.execute('''INSERT INTO attendance(student_id, attendance_date, status) VALUES(?,?,?)
                ON CONFLICT(student_id, attendance_date) DO UPDATE SET status=excluded.status''',
                (student['id'], attendance_date, status))
    flash('Attendance saved for ' + attendance_date + '.', 'success')
    return redirect(url_for('dashboard', date=attendance_date))


@app.route('/reports')
@login_required
def reports():
    with db() as con:
        report_rows = con.execute('''SELECT s.id, s.usn, s.name, s.department, s.semester,
            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS attended,
            COUNT(a.id) AS total
            FROM students s LEFT JOIN attendance a ON s.id=a.student_id
            GROUP BY s.id ORDER BY s.usn''').fetchall()
    rows = []
    for r in report_rows:
        attended = r['attended'] or 0
        total = r['total'] or 0
        percent = round((attended / total * 100), 1) if total else 0
        rows.append({**dict(r), 'attended': attended, 'total': total, 'percent': percent})
    return render_template('reports.html', rows=rows)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



init_db()

if __name__ == '__main__':
    app.run(debug=True)
