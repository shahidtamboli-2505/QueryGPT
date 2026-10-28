from app.database.db import initialize, connect, schema_info

def test_seed_and_persistence(tmp_path):
    path=tmp_path/'persist.db'; initialize(path)
    c=connect(path); n=c.execute('SELECT COUNT(*) FROM students').fetchone()[0]; c.execute("INSERT INTO students VALUES(99,'Test Person','Testing',1,'persist@example.edu','Pune')"); c.commit(); c.close()
    initialize(path); c=connect(path)
    assert c.execute('SELECT COUNT(*) FROM students').fetchone()[0]==n+1
    assert c.execute("SELECT name FROM students WHERE id=99").fetchone()[0]=='Test Person'; c.close()

def test_foreign_keys_present(tmp_path):
    path=tmp_path/'schema.db'; initialize(path)
    tables={t['name']:t for t in schema_info(path)}
    assert tables['enrollments']['foreign_keys']
