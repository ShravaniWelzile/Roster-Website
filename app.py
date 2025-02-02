from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Create Employees Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                shifts TEXT
            )
        ''')

        # 🔹 Drop old schedule table to fix missing column issue
        cursor.execute('DROP TABLE IF EXISTS schedule')

        # Create Schedule Table with `weekend_shift` column
        cursor.execute('''
            CREATE TABLE schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                shift TEXT,
                date TEXT,
                weekend_shift TEXT DEFAULT 'No',
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        conn.commit()

        # Preload employees
        employees = [
            ("Alice", "day,night"),
            ("Bob", "day"),
            ("Charlie", "night"),
            ("David", "day,night"),
            ("Eve", "day"),
            ("Frank", "night"),
            ("Grace", "day,night"),
            ("Hank", "day"),
            ("Ivy", "night"),
            ("Jack", "day,night")
        ]
        cursor.execute('DELETE FROM employees')  # Clear existing employees
        cursor.executemany('INSERT INTO employees (name, shifts) VALUES (?, ?)', employees)
        conn.commit()

# Home page - Now passes employees to template
@app.route('/')
def home():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        employees = cursor.execute('SELECT * FROM employees').fetchall()
    return render_template('index.html', employees=employees)

# Generate schedule (Re-added so user can select employees)
@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schedule')  # Clear old schedule

        employee_ids = request.form.getlist('employee_ids')
        date = request.form['date']

        for emp_id in employee_ids:
            shift = request.form.get(f'shift_{emp_id}', 'day')  # Default to day shift
            weekend_shift = 'Yes' if f'weekend_{emp_id}' in request.form else 'No'
            
            cursor.execute('''
                INSERT INTO schedule (employee_id, shift, date, weekend_shift)
                VALUES (?, ?, ?, ?)
            ''', (emp_id, shift, date, weekend_shift))

        conn.commit()
    return redirect(url_for('home'))

# View schedule
@app.route('/view_schedule')
def view_schedule():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        schedule = cursor.execute('''
            SELECT employees.name, schedule.shift, schedule.date, schedule.weekend_shift
            FROM schedule
            JOIN employees ON schedule.employee_id = employees.id
        ''').fetchall()
    return render_template('schedule.html', schedule=schedule)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
