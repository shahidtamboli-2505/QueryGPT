from pydantic import BaseModel, Field
from typing import Any

class QuestionRequest(BaseModel): question: str = Field(min_length=3, max_length=1000)
class ExecuteRequest(BaseModel): sql: str = Field(min_length=1, max_length=10000); question: str = Field(default="Manual SQL execution", max_length=1000); mode: str = "manual"
class GenerateResponse(BaseModel): question: str; sql: str; mode: str
class QueryResponse(BaseModel): question: str; sql: str | None; columns: list[str]; rows: list[dict[str, Any]]; result_count: int; execution_ms: float; status: str; mode: str; error: str | None = None
