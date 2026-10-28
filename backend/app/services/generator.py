import json
import re
import urllib.request
import urllib.error
from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from app.database.db import schema_info

class GenerationError(ValueError): pass

def demo_generate(question: str) -> str:
    q = re.sub(r"\s+", " ", question.lower()).strip().rstrip("?.!")
    # Deterministic examples only: explicitly disclosed demo mode.
    patterns = [
      (r"^(show|list|get) all students$", "SELECT * FROM students ORDER BY id"),
      (r"(student|people).*(scor\w*|mark).*(more than|above|over|greater than)\s*(\d+)", None),
      (r"(count|number of) students.*department|students in each department", "SELECT department, COUNT(*) AS student_count FROM students GROUP BY department ORDER BY student_count DESC"),
      (r"average marks.*course|average.*marks.*each course", "SELECT c.course_name, ROUND(AVG(e.marks), 2) AS average_marks FROM courses c JOIN enrollments e ON e.course_id = c.id GROUP BY c.id, c.course_name ORDER BY average_marks DESC"),
      (r"top (\d+) students?.*(mark|score)|top five students?.*(mark|score)", None),
      (r"highest.*lowest.*marks|highest and lowest marks", "SELECT MAX(marks) AS highest_marks, MIN(marks) AS lowest_marks FROM enrollments"),
      (r"(list|show|display).*students.*(enrolled|each course)|students enrolled in each course", "SELECT c.course_name, s.name AS student_name, e.marks, e.grade FROM enrollments e JOIN students s ON s.id=e.student_id JOIN courses c ON c.id=e.course_id ORDER BY c.course_name, s.name"),
      (r"students.*each academic year|count students.*year|students in each year", "SELECT year, COUNT(*) AS student_count FROM students GROUP BY year ORDER BY year"),
      (r"courses?.*(average|avg).*(exceed|above|greater than)\s*(\d+)", None),
      (r"^(show|list|get) all courses$", "SELECT * FROM courses ORDER BY id"),
      (r"^(show|list|get) all enrollments$", "SELECT * FROM enrollments ORDER BY id"),
    ]
    for pattern, sql in patterns:
        m = re.search(pattern, q)
        if not m: continue
        if pattern.startswith("(student"):
            threshold = int(m.group(4)); return f"SELECT s.id, s.name, s.department, c.course_name, e.marks, e.grade FROM enrollments e JOIN students s ON s.id=e.student_id JOIN courses c ON c.id=e.course_id WHERE e.marks > {threshold} ORDER BY e.marks DESC"
        if "top (\\d+)" in pattern:
            n = int(m.group(1)) if m.group(1) else 5
            return f"SELECT s.id, s.name, s.department, c.course_name, e.marks FROM enrollments e JOIN students s ON s.id=e.student_id JOIN courses c ON c.id=e.course_id ORDER BY e.marks DESC LIMIT {min(n, 50)}"
        if "courses?.*(average|avg)" in pattern:
            threshold = int(m.group(4)); return f"SELECT c.course_name, ROUND(AVG(e.marks), 2) AS average_marks FROM courses c JOIN enrollments e ON e.course_id=c.id GROUP BY c.id, c.course_name HAVING AVG(e.marks) > {threshold} ORDER BY average_marks DESC"
        return sql
    raise GenerationError("Demo mode supports common student, course, enrollment, marks, department, year, join, and aggregation questions. Configure an LLM API key or try one of the example prompts.")

def generate_sql(question: str):
    if not LLM_API_KEY: return demo_generate(question), "demo"
    schema = schema_info()
    prompt = ("Convert the user's question to exactly one SQLite SELECT statement. Use only tables and columns in the schema. "
      "Do not use markdown fences or explanations. Never generate writes, PRAGMA, ATTACH, or external database references. "
      "Schema JSON: " + json.dumps(schema) + "\nQuestion: " + question)
    payload = json.dumps({"model": LLM_MODEL, "temperature": 0, "messages": [{"role":"system","content":"You generate safe SQLite SELECT queries only."},{"role":"user","content":prompt}]}).encode()
    req = urllib.request.Request(LLM_BASE_URL + "/chat/completions", data=payload, headers={"Authorization":"Bearer " + LLM_API_KEY,"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as response: data = json.loads(response.read().decode())
        sql = data["choices"][0]["message"]["content"].strip()
        sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql, flags=re.I).strip()
        return sql, "llm"
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, ValueError, json.JSONDecodeError):
        raise GenerationError("The configured AI provider could not generate SQL. Check provider settings and connectivity, or remove the key to use demo mode.") from None
