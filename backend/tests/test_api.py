def test_health_and_schema(client):
    assert client.get('/api/health').status_code == 200
    schema=client.get('/api/schema').json()['tables']
    assert {t['name'] for t in schema} >= {'students','courses','enrollments'}
    assert next(t for t in schema if t['name']=='students')['row_count'] >= 20

def test_filter_aggregation_join(client):
    assert client.post('/api/execute',json={'sql':'SELECT * FROM students WHERE year > 2'}).status_code == 200
    assert client.post('/api/execute',json={'sql':'SELECT department, COUNT(*) n FROM students GROUP BY department'}).json()['result_count'] >= 1
    assert client.post('/api/execute',json={'sql':'SELECT s.name,c.course_name,e.marks FROM students s JOIN enrollments e ON e.student_id=s.id JOIN courses c ON c.id=e.course_id'}).status_code == 200

def test_unsafe_and_multiple_statements_rejected(client):
    for sql in ['DELETE FROM students','DROP TABLE students','SELECT 1; SELECT 2','PRAGMA table_info(students)','UPDATE students SET name="x"']:
        assert client.post('/api/execute',json={'sql':sql}).status_code == 400

def test_bad_table_and_column(client):
    assert client.post('/api/execute',json={'sql':'SELECT * FROM nonexistent'}).status_code == 400
    assert client.post('/api/execute',json={'sql':'SELECT missing FROM students'}).status_code == 400

def test_generate_demo_and_query_history(client, monkeypatch):
    import app.main as mainmod
    monkeypatch.setattr(mainmod, 'generate_sql', lambda q: ('SELECT * FROM students', 'demo'))
    response=client.post('/api/query',json={'question':'Show all students'})
    assert response.status_code == 200 and response.json()['result_count'] >= 20
    history=client.get('/api/history').json()['items']
    assert history and history[0]['question']=='Show all students'
    assert client.get('/api/history/'+str(history[0]['id'])).status_code == 200

def test_csv_export(client):
    r=client.get('/api/export.csv',params={'sql':'SELECT id,name FROM students LIMIT 2'})
    assert r.status_code == 200 and 'text/csv' in r.headers['content-type'] and 'name' in r.text

def test_tables_endpoint_and_not_found(client):
    assert client.get('/api/tables').status_code == 200
    assert client.get('/api/tables/students').status_code == 200
    assert client.get('/api/tables/not_a_table').status_code == 404
