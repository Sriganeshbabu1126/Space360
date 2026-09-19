import os

filepath = r"backend\app\schemas.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_schema = """class SiteResponse(BaseModel):
    id: str
    name: str
    address: Optional[str]
    gps_bounds: Optional[dict]
    org_id: Optional[str]
    created_by: str
    status: StatusEnum
    created_at: datetime
    open_issues_count: int = 0"""
new_schema = """class SiteResponse(BaseModel):
    id: str
    name: str
    address: Optional[str]
    gps_bounds: Optional[dict]
    org_id: Optional[str]
    created_by: str
    status: StatusEnum
    created_at: datetime
    open_issues_count: int = 0
    floor_plan_url: Optional[str] = None"""
if old_schema in content:
    content = content.replace(old_schema, new_schema)
else:
    print("Could not find SiteResponse in schemas.py")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
