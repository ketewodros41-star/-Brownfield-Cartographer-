import os
import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal

NodeType = Literal["Module", "Dataset", "Function", "Transformation"]
EdgeType = Literal["IMPORTS", "PRODUCES", "CONSUMES", "CALLS", "CONFIGURES"]

class NodeMetadata(BaseModel):
    file_path: str
    line_range: Optional[tuple] = None
    analysis_method: str
    confidence: float = 1.0

class CodeNode(BaseModel):
    id: str
    type: NodeType
    metadata: NodeMetadata
    properties: Dict[str, Any] = Field(default_factory=dict)

class Edge(BaseModel):
    source: str
    target: str
    type: EdgeType
    metadata: Optional[Dict[str, Any]] = None

class CartographyTrace(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    agent: str
    operation: str
    evidence: Any
    confidence: float
