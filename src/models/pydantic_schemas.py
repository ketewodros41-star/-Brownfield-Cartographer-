from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

NodeType = Literal["Module", "Dataset", "Function", "Transformation"]
EdgeType = Literal["IMPORTS", "PRODUCES", "CONSUMES", "CALLS", "CONFIGURES"]

class ModuleNode(BaseModel):
    path: str
    language: str
    purpose_statement: Optional[str] = None
    domain_cluster: Optional[str] = None
    complexity_score: Optional[float] = None
    change_velocity_30d: Optional[int] = None
    is_dead_code_candidate: bool = False
    last_modified: datetime = Field(default_factory=datetime.now)

class DatasetNode(BaseModel):
    name: str
    storage_type: str  # [table|file|stream|api]
    schema_snapshot: Optional[Dict[str, str]] = None
    freshness_sla: Optional[str] = None
    owner: Optional[str] = None
    is_source_of_truth: bool = False

class FunctionNode(BaseModel):
    qualified_name: str
    parent_module: str
    signature: str
    purpose_statement: Optional[str] = None
    call_count_within_repo: int = 0
    is_public_api: bool = True

class TransformationNode(BaseModel):
    source_datasets: List[str]
    target_datasets: List[str]
    transformation_type: str
    source_file: str
    line_range: List[int]  # Changed Tuple to List for simpler serialization
    sql_query_if_applicable: Optional[str] = None

class Edge(BaseModel):
    source: str
    target: str
    type: EdgeType  # IMPORTS, PRODUCES, CONSUMES, CALLS, CONFIGURES
    metadata: Dict[str, Any] = Field(default_factory=dict)

