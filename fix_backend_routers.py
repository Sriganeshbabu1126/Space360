import os
import re

filepath = r"backend\app\routers\sites.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_loop = """        count = db.query(Issue)\\
                  .join(LocationPoint, Issue.location_id == LocationPoint.id)\\
                  .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id)\\
                  .filter(FloorPlan.site_id == site.id)\\
                  .filter(Issue.status != IssueStatusEnum.closed)\\
                  .count()
        
        site_dict = {
            "id": site.id,
            "name": site.name,
            "address": site.address,
            "gps_bounds": site.gps_bounds,
            "org_id": site.org_id,
            "created_by": site.created_by,
            "status": site.status,
            "created_at": site.created_at,
            "open_issues_count": count
        }"""
new_loop = """        count = db.query(Issue)\\
                  .join(LocationPoint, Issue.location_id == LocationPoint.id)\\
                  .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id)\\
                  .filter(FloorPlan.site_id == site.id)\\
                  .filter(Issue.status != IssueStatusEnum.closed)\\
                  .count()
        
        first_floor_plan = db.query(FloorPlan).filter(FloorPlan.site_id == site.id).first()
        floor_plan_url = first_floor_plan.image_url if first_floor_plan else None
        
        site_dict = {
            "id": site.id,
            "name": site.name,
            "address": site.address,
            "gps_bounds": site.gps_bounds,
            "org_id": site.org_id,
            "created_by": site.created_by,
            "status": site.status,
            "created_at": site.created_at,
            "open_issues_count": count,
            "floor_plan_url": floor_plan_url
        }"""

if old_loop in content:
    content = content.replace(old_loop, new_loop)
else:
    print("Could not find old_loop in sites.py")

# Also need to check get_site
old_get = """def get_site(site_id: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    count = db.query(Issue)\\
              .join(LocationPoint, Issue.location_id == LocationPoint.id)\\
              .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id)\\
              .filter(FloorPlan.site_id == site.id)\\
              .filter(Issue.status != IssueStatusEnum.closed)\\
              .count()
              
    return {
        "id": site.id,
        "name": site.name,
        "address": site.address,
        "gps_bounds": site.gps_bounds,
        "org_id": site.org_id,
        "created_by": site.created_by,
        "status": site.status,
        "created_at": site.created_at,
        "open_issues_count": count
    }"""
new_get = """def get_site(site_id: str, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    count = db.query(Issue)\\
              .join(LocationPoint, Issue.location_id == LocationPoint.id)\\
              .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id)\\
              .filter(FloorPlan.site_id == site.id)\\
              .filter(Issue.status != IssueStatusEnum.closed)\\
              .count()
              
    first_floor_plan = db.query(FloorPlan).filter(FloorPlan.site_id == site.id).first()
    floor_plan_url = first_floor_plan.image_url if first_floor_plan else None
              
    return {
        "id": site.id,
        "name": site.name,
        "address": site.address,
        "gps_bounds": site.gps_bounds,
        "org_id": site.org_id,
        "created_by": site.created_by,
        "status": site.status,
        "created_at": site.created_at,
        "open_issues_count": count,
        "floor_plan_url": floor_plan_url
    }"""
if old_get in content:
    content = content.replace(old_get, new_get)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
