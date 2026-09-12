import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add JSON import if needed
if "import kotlinx.serialization.json.Json" not in content:
    content = content.replace("import kotlinx.coroutines.launch", "import kotlinx.coroutines.launch\nimport kotlinx.serialization.json.Json\nimport com.sgbdevapps.space360.data.remote.AddCommentRequest")

old_load = """                val mapped = issuesList.map { 
                    Issue(
                        id = it.id,
                        title = it.title,
                        description = it.description ?: "",
                        status = it.status,
                        priority = it.priority ?: "",
                        siteId = it.site_id ?: "",
                        assignedTo = "",
                        assignedToName = "",
                        createdAt = it.created_at ?: "",
                        updatedAt = it.updated_at ?: "",
                        comments = emptyList() // simplified
                    )
                }
                _issues.value = mapped"""
new_load = """                val mapped = issuesList.map { 
                    var finalStatus = it.status
                    try {
                        val pending = offlineSyncManager.getPendingItemsForResource("issue", it.id)
                        pending.forEach { action ->
                            if (action.action == "update_status") {
                                try {
                                    val req = Json.decodeFromString<UpdateIssueStatusRequest>(action.payload)
                                    finalStatus = req.status
                                } catch(e:Exception){}
                            }
                        }
                    } catch(e:Exception){}
                
                    Issue(
                        id = it.id,
                        title = it.title,
                        description = it.description ?: "",
                        status = finalStatus,
                        priority = it.priority ?: "",
                        siteId = it.site_id ?: "",
                        assignedTo = "",
                        assignedToName = "",
                        createdAt = it.created_at ?: "",
                        updatedAt = it.updated_at ?: "",
                        comments = emptyList() // simplified
                    )
                }
                _issues.value = mapped"""
if old_load in content:
    content = content.replace(old_load, new_load)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
