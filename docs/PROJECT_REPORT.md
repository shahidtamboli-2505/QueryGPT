# QueryGPT: Automated SQL Query Generation from Natural Language

## Abstract
QueryGPT is a local web application that helps users retrieve structured academic information by writing questions in natural language. It generates SQL using deterministic demo rules or an optional configurable LLM API, validates the SQL with SQLGlot, executes approved read-only queries against SQLite, and presents results in a searchable interface with CSV export and persistent history.

## Introduction
Relational databases commonly require users to know SQL syntax and schema details. QueryGPT provides a simpler interface for exploring sample academic records while preserving SQL visibility and validation.

## Problem statement
Users who do not know SQL may find it difficult to filter, join, group, and aggregate relational data. A natural-language interface can reduce the syntax barrier, but generated SQL must be validated before it reaches a database.

## Objectives
- Convert supported natural-language questions to SQL.
- Use actual database schema in the generation workflow.
- Execute read-only SQL and display real results.
- Inspect tables and relationships.
- Preserve query history across restarts.
- Provide CSV export, error handling, and automated tests.

## Existing system
Traditional database tools expect users to compose SQL manually. Generic AI chat tools may produce SQL without executing it against the user's actual schema or without a controlled execution path.

## Proposed system
QueryGPT combines a React UI, FastAPI service, SQLite storage, SQLGlot AST validation, a deterministic no-key demo generator, and optional LLM integration. All result rows come from database execution.

## Technology stack
- Frontend: React, TypeScript, Vite, CSS, Lucide React.
- Backend: Python, FastAPI, Pydantic, Uvicorn.
- Data: SQLite with foreign keys and persistent query history.
- SQL validation: SQLGlot.
- Testing: Pytest and FastAPI TestClient.
- Optional AI: OpenAI-compatible chat-completions API configured through backend environment variables.

## System architecture
See `ARCHITECTURE.md` for the architecture and ER diagrams. The browser sends JSON requests to FastAPI. Generation uses the schema, SQL passes through a parser/guard, and permitted SQL runs on a read-only SQLite connection. Query status and metadata are saved to history.

## Database schema
`students(id, name, department, year, email, city)` stores 24 fictional student records. `courses(id, course_name, credits, department)` stores seven courses. `enrollments(id, student_id, course_id, semester, marks, grade)` connects students and courses using foreign keys. `query_history` stores the submitted question, SQL, status, mode, result count, duration, error, and timestamp. Sample data is seeded only when the students table is empty.

## Module descriptions
1. Dashboard: actual history statistics, connection status, recent activity, and table shortcuts.
2. Query Playground: prompt input, SQL editor, generation/execution, searchable rows, timing, and CSV export.
3. Database Explorer: table previews and row counts.
4. Schema Viewer: columns, primary keys, foreign keys, and relationships.
5. Query History: saved executions and reopening a prompt/SQL.
6. Settings: database health and AI mode/configuration guidance.

## Implementation methodology
The application is split into UI, API, generation, validation, database, and testing modules. The backend initializes schema and sample records, generates or accepts SQL, parses the statement, executes it read-only, and stores the outcome. The frontend calls live API endpoints and renders returned values.

## SQL validation and security
SQLGlot parses the SQL as SQLite syntax. Exactly one SELECT-family statement is accepted. Common DDL/DML, PRAGMA, external database qualification, and selected unsafe functions are rejected. Queries execute through a read-only SQLite URI. Results are capped. API keys remain in backend environment variables. These controls are appropriate for a local educational demo but do not constitute a complete production security boundary against every SQLite feature or denial-of-service query.

## Testing
Automated tests cover seed/persistence, foreign keys, health/schema endpoints, table previews, filtering, aggregation, joins, invalid table/column references, prohibited operations, multiple statements, history, and CSV output. Actual pass/fail counts should be reported only after running the test suite in the target environment.

## Results
The intended working result is a local interface that executes safe SQL against the seeded SQLite database and displays the returned records. Record actual test/build outcomes after executing the commands in the README; no accuracy score is claimed because the project does not train a model.

## Limitations
- Demo generation supports a finite list of common question patterns, not arbitrary language.
- Live generation requires a compatible provider, credentials, network access, and may incur provider charges.
- SQL validation is defense-in-depth, not a substitute for process isolation in production.
- The local app is designed for a single developer machine and has no authentication or multi-user permissions.
- Schema references are ultimately validated by SQLite at execution time.

## Future scope
- Add local models, richer intent classification, schema-aware retrieval, query explanation, pagination, database import, authentication, role-based access, more database engines, and expanded adversarial SQL tests.

## Conclusion
QueryGPT demonstrates an end-to-end natural-language-to-SQL workflow with a real relational database, guarded read-only execution, visible SQL, result visualization, query history, and CSV export. Its no-key demo mode makes the core workflow available for classroom demonstrations while clearly distinguishing deterministic rules from live LLM generation.

## References
- FastAPI documentation: https://fastapi.tiangolo.com/
- React documentation: https://react.dev/
- Vite documentation: https://vite.dev/
- SQLite documentation: https://www.sqlite.org/docs.html
- SQLGlot documentation: https://sqlglot.com/sqlglot.html
- Pytest documentation: https://docs.pytest.org/
