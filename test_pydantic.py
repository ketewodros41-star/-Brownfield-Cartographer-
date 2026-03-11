from src.models.pydantic_schemas import ModuleNode, Edge
print("Pydantic models loaded successfully")
m = ModuleNode(path="test.py", language="python")
print(m)
e = Edge(source="a", target="b", type="IMPORTS")
print(e)
