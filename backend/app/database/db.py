import sqlite3
from pathlib import Path
from app.config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, department TEXT NOT NULL,
 year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4), email TEXT UNIQUE NOT NULL, city TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS courses (
 id INTEGER PRIMARY KEY, course_name TEXT NOT NULL, credits INTEGER NOT NULL, department TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS enrollments (
 id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id),
 course_id INTEGER NOT NULL REFERENCES courses(id), semester TEXT NOT NULL,
 marks REAL NOT NULL CHECK(marks BETWEEN 0 AND 100), grade TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS query_history (
 id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, generated_sql TEXT,
 status TEXT NOT NULL, mode TEXT NOT NULL, result_count INTEGER NOT NULL DEFAULT 0,
 execution_ms REAL, error TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);
"""

FIRST_NAMES = ["Aarav", "Aditi", "Vihaan", "Anaya", "Ishaan", "Saanvi", "Reyansh", "Diya", "Arjun", "Myra", "Kabir", "Sara", "Advait", "Ira", "Rohan", "Meera", "Dev", "Kiara", "Neil", "Tara", "Om", "Riya", "Yash", "Pooja"]
LAST_NAMES = ["Patil", "Sharma", "Kulkarni", "Deshmukh", "Joshi", "Shah", "Pawar", "More", "Kadam", "Jadhav", "Naik", "Bhosale"]
DEPARTMENTS = ["AI & Data Science", "Computer Science", "Information Technology", "Electronics"]
CITIES = ["Pune", "Sangli", "Kolhapur", "Mumbai", "Nashik", "Satara"]
COURSES = [("Machine Learning", 4, "AI & Data Science"), ("Database Systems", 3, "Computer Science"), ("Natural Language Processing", 4, "AI & Data Science"), ("Computer Networks", 3, "Information Technology"), ("Web Development", 3, "Information Technology"), ("Data Visualization", 3, "AI & Data Science"), ("Operating Systems", 4, "Computer Science")]

def connect(path=None, readonly=False):
    db_path = Path(path or DATABASE_PATH)
    if readonly:
        conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True, timeout=2)
    else:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), timeout=2)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize(path=None):
    conn = connect(path)
    try:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            for i in range(24):
                name = f"{FIRST_NAMES[i]} {LAST_NAMES[(i * 3) % len(LAST_NAMES)]}"
                dept = DEPARTMENTS[i % len(DEPARTMENTS)]
                conn.execute("INSERT INTO students(id,name,department,year,email,city) VALUES(?,?,?,?,?,?)",
                    (i + 1, name, dept, i % 4 + 1, f"student{i+1:02d}@example.edu", CITIES[i % len(CITIES)]))
            for i, course in enumerate(COURSES, 1):
                conn.execute("INSERT INTO courses(id,course_name,credits,department) VALUES(?,?,?,?)", (i, *course))
            eid = 1
            for sid in range(1, 25):
                # Each student takes three courses; deterministic but varied marks.
                for offset in range(3):
                    cid = (sid + offset - 1) % len(COURSES) + 1
                    marks = float(45 + ((sid * 13 + cid * 7) % 56))
                    grade = "A" if marks >= 85 else "B" if marks >= 70 else "C" if marks >= 55 else "D"
                    conn.execute("INSERT INTO enrollments VALUES(?,?,?,?,?,?)", (eid, sid, cid, "Sem 1" if sid % 2 else "Sem 2", marks, grade))
                    eid += 1
        conn.commit()
    finally:
        conn.close()

def schema_info(path=None):
    conn = connect(path, readonly=True)
    try:
        tables = []
        for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            name = t[0]
            cols = [dict(name=r[1], type=r[2], notnull=bool(r[3]), default=r[4], primary_key=bool(r[5])) for r in conn.execute(f'PRAGMA table_info("{name}")')]
            fks = [dict(from_column=r[3], to_table=r[2], to_column=r[4]) for r in conn.execute(f'PRAGMA foreign_key_list("{name}")')]
            count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            tables.append(dict(name=name, columns=cols, foreign_keys=fks, row_count=count))
        return tables
    finally: conn.close()
