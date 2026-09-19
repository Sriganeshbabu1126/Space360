import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiModels.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_resp = """data class SiteResponse(
    val id: String,
    val name: String,
    @SerializedName("address") val location: String? = null,
    val status: String = "Active",
    val open_issues_count: Int = 0
)"""
new_resp = """data class SiteResponse(
    val id: String,
    val name: String,
    @SerializedName("address") val location: String? = null,
    val status: String = "Active",
    val open_issues_count: Int = 0,
    val floor_plan_url: String? = null
)"""
if old_resp in content:
    content = content.replace(old_resp, new_resp)
else:
    print("Could not find SiteResponse in ApiModels.kt")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
