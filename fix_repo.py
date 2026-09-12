import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/repository/SiteRepositoryImpl.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_map = """            val sites = response.map {
                Site(
                    id = it.id,
                    name = it.name,
                    location = it.location,
                    status = it.status,
                    openIssuesCount = it.open_issues_count
                )
            }"""
new_map = """            val sites = response.map {
                Site(
                    id = it.id,
                    name = it.name,
                    location = it.location,
                    status = it.status,
                    openIssuesCount = it.open_issues_count,
                    floorPlanUrl = it.floor_plan_url
                )
            }"""
if old_map in content:
    content = content.replace(old_map, new_map)
else:
    print("Could not find getAssignedSites map block")

old_map2 = """                val site = Site(
                    id = response.id,
                    name = response.name,
                    location = response.location,
                    status = response.status,
                    openIssuesCount = response.open_issues_count
                )"""
new_map2 = """                val site = Site(
                    id = response.id,
                    name = response.name,
                    location = response.location,
                    status = response.status,
                    openIssuesCount = response.open_issues_count,
                    floorPlanUrl = response.floor_plan_url
                )"""
if old_map2 in content:
    content = content.replace(old_map2, new_map2)
else:
    print("Could not find getSiteById map block")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
