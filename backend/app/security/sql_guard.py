import sqlglot
from sqlglot import exp
from app.config import MAX_RESULT_ROWS

class SQLValidationError(ValueError): pass

BLOCKED = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter, exp.Create, exp.Command,
           exp.Transaction, exp.Merge, exp.TruncateTable, exp.Grant, exp.Revoke)

def validate_select(sql: str) -> str:
    if not isinstance(sql, str) or not sql.strip(): raise SQLValidationError("SQL query is empty.")
    try: statements = sqlglot.parse(sql, read="sqlite")
    except Exception as exc: raise SQLValidationError(f"Could not parse SQL: {str(exc).splitlines()[0][:180]}") from None
    statements = [s for s in statements if s is not None]
    if len(statements) != 1: raise SQLValidationError("Only one SQL statement is allowed.")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Subquery, exp.Union, exp.Intersect, exp.Except)):
        raise SQLValidationError("Only read-only SELECT queries (including safe CTEs) are allowed.")
    for node in tree.walk():
        if isinstance(node, BLOCKED): raise SQLValidationError(f"Unsupported or unsafe SQL operation: {node.key.upper()}.")
        if isinstance(node, exp.Anonymous) and node.name.lower() in {"load_extension", "writefile", "readfile"}:
            raise SQLValidationError("This SQL function is not allowed.")
        if isinstance(node, exp.Pragma): raise SQLValidationError("PRAGMA statements are not allowed.")
        if isinstance(node, exp.Table) and node.db:
            raise SQLValidationError("Qualified external databases are not allowed.")
    # Add a bounded LIMIT if absent; clamp an oversized literal LIMIT.
    limit = tree.args.get("limit")
    if limit is None:
        tree = tree.limit(MAX_RESULT_ROWS)
    elif isinstance(limit.expression, exp.Literal) and not limit.expression.is_string:
        try: requested = int(limit.expression.this)
        except (ValueError, TypeError): requested = MAX_RESULT_ROWS
        if requested > MAX_RESULT_ROWS: tree.set("limit", exp.Limit(expression=exp.Literal.number(MAX_RESULT_ROWS)))
    return tree.sql(dialect="sqlite")
