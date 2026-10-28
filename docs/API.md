# QueryGPT API
Base URL: `http://127.0.0.1:8000`
Interactive documentation: `/docs`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API, database, and AI-mode status |
| GET | `/api/schema` | Table/column metadata, row counts, foreign keys |
| GET | `/api/tables` | Academic table list |
| GET | `/api/tables/{table_name}?limit=20` | Table preview and count |
| POST | `/api/generate` | Generate and validate SQL without executing |
| POST | `/api/execute` | Validate and execute supplied SELECT SQL |
| POST | `/api/query` | Generate, validate, execute, and persist history |
| GET | `/api/history?limit=100` | Recent query history |
| GET | `/api/history/{query_id}` | One history record |
| GET | `/api/export.csv?sql=...` | Validate and export SELECT results as CSV |

## Request bodies
`POST /api/generate` and `POST /api/query`:
```json
{"question":"Count students in each department"}
```
`POST /api/execute`:
```json
{"question":"Preview students","sql":"SELECT id, name FROM students LIMIT 10","mode":"manual"}
```

## Error behavior
- `422`: invalid request fields, unsupported demo prompt, or generated SQL rejected by validation.
- `400`: unsafe/invalid SQL or database execution error.
- `404`: unknown table or history identifier.

Successful query response includes `question`, `sql`, `columns`, `rows`, `result_count`, `execution_ms`, `status`, `mode`, and `error`.
