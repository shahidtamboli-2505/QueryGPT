import csv, io, sqlite3, time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.config import FRONTEND_ORIGIN, MAX_RESULT_ROWS, QUERY_TIMEOUT_SECONDS, LLM_API_KEY, LLM_MODEL
from app.database.db import initialize, connect, schema_info
from app.schemas.models import QuestionRequest, ExecuteRequest
from app.services.generator import generate_sql, GenerationError
from app.security.sql_guard import validate_select, SQLValidationError

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield
app = FastAPI(title="QueryGPT API", version="1.0.0", description="Natural language to safe, read-only SQL for a local academic database.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list({FRONTEND_ORIGIN,"http://localhost:5173","http://127.0.0.1:5173"}), allow_credentials=True, allow_methods=["GET","POST","OPTIONS"], allow_headers=["*"])

@app.get("/api/health")
def health():
    try:
        conn=connect(readonly=True); conn.execute("SELECT 1").fetchone(); conn.close(); db="connected"
    except Exception: db="disconnected"
    return {"status":"ok" if db=="connected" else "degraded","database":db,"ai_mode":"llm" if LLM_API_KEY else "demo","ai_configured":bool(LLM_API_KEY),"model":LLM_MODEL if LLM_API_KEY else None}

@app.get("/api/schema")
def get_schema(): return {"tables":schema_info()}
@app.get("/api/tables")
def get_tables(): return {"tables":[{"name":t["name"],"row_count":t["row_count"]} for t in schema_info() if t["name"] != "query_history"]}

@app.get("/api/tables/{table_name}")
def get_table(table_name: str, limit: int = Query(20, ge=1, le=100)):
    allowed={t["name"] for t in schema_info() if t["name"] in {"students","courses","enrollments"}}
    if table_name not in allowed: raise HTTPException(404,"Table not found.")
    conn=connect(readonly=True)
    try:
        columns=[r[1] for r in conn.execute(f'PRAGMA table_info("{table_name}")')]
        rows=[dict(r) for r in conn.execute(f'SELECT * FROM "{table_name}" LIMIT ?', (limit,))]
        count=conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
        return {"name":table_name,"columns":columns,"rows":rows,"row_count":count}
    finally: conn.close()

def run_sql(sql, question, mode):
    started=time.perf_counter()
    try:
        safe_sql=validate_select(sql)
        conn=connect(readonly=True)
        conn.set_progress_handler(lambda: 1 if time.perf_counter() - started > QUERY_TIMEOUT_SECONDS else 0, 1000)
        try:
            cur=conn.execute(safe_sql)
            columns=[d[0] for d in (cur.description or [])]
            rows=[dict(r) for r in cur.fetchmany(MAX_RESULT_ROWS)]
        finally: conn.close()
        elapsed=round((time.perf_counter()-started)*1000,2)
        save_history(question,safe_sql,"success",mode,len(rows),elapsed,None)
        return {"question":question,"sql":safe_sql,"columns":columns,"rows":rows,"result_count":len(rows),"execution_ms":elapsed,"status":"success","mode":mode,"error":None}
    except (SQLValidationError, sqlite3.Error) as exc:
        elapsed=round((time.perf_counter()-started)*1000,2)
        msg=str(exc)[:300]
        save_history(question,sql,"failed",mode,0,elapsed,msg)
        return {"question":question,"sql":sql,"columns":[],"rows":[],"result_count":0,"execution_ms":elapsed,"status":"failed","mode":mode,"error":msg}

def save_history(question, sql, status, mode, count, ms, error):
    conn=connect()
    try:
        conn.execute("INSERT INTO query_history(question,generated_sql,status,mode,result_count,execution_ms,error) VALUES(?,?,?,?,?,?,?)",(question,sql,status,mode,count,ms,error)); conn.commit()
    finally: conn.close()

@app.post("/api/generate")
def generate(body: QuestionRequest):
    try:
        sql,mode=generate_sql(body.question)
        sql=validate_select(sql)
        return {"question":body.question,"sql":sql,"mode":mode}
    except GenerationError as exc: raise HTTPException(422,str(exc))
    except SQLValidationError as exc: raise HTTPException(422,f"Generated SQL was rejected by the safety validator: {exc}")

@app.post("/api/execute")
def execute(body: ExecuteRequest):
    result=run_sql(body.sql,body.question,body.mode)
    if result["status"]=="failed": raise HTTPException(400,detail={"message":result["error"],"result":result})
    return result

@app.post("/api/query")
def query(body: QuestionRequest):
    try: sql,mode=generate_sql(body.question)
    except GenerationError as exc:
        save_history(body.question,None,"failed","demo" if not LLM_API_KEY else "llm",0,0,str(exc))
        raise HTTPException(422,str(exc))
    result=run_sql(sql,body.question,mode)
    if result["status"]=="failed": raise HTTPException(400,detail={"message":result["error"],"result":result})
    return result

@app.get("/api/history")
def history(limit: int = Query(100, ge=1, le=500)):
    conn=connect(readonly=True)
    try: return {"items":[dict(r) for r in conn.execute("SELECT * FROM query_history ORDER BY id DESC LIMIT ?",(limit,))]}
    finally: conn.close()
@app.get("/api/history/{query_id}")
def history_item(query_id: int):
    conn=connect(readonly=True)
    try:
        row=conn.execute("SELECT * FROM query_history WHERE id=?",(query_id,)).fetchone()
        if not row: raise HTTPException(404,"History item not found.")
        return dict(row)
    finally: conn.close()
@app.get("/api/export.csv")
def export_csv(sql: str = Query(..., min_length=1, max_length=10000)):
    try: safe=validate_select(sql)
    except SQLValidationError as exc: raise HTTPException(400,str(exc))
    conn=connect(readonly=True)
    try:
        cur=conn.execute(safe); rows=cur.fetchmany(MAX_RESULT_ROWS); cols=[d[0] for d in cur.description or []]
        out=io.StringIO(); writer=csv.writer(out); writer.writerow(cols)
        for row in rows: writer.writerow([row[c] for c in cols])
        return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=querygpt-results.csv"})
    except sqlite3.Error as exc: raise HTTPException(400,str(exc)[:250])
    finally: conn.close()
