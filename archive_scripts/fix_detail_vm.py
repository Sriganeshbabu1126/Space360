import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add JSON import
if "import kotlinx.serialization.json.Json" not in content:
    content = content.replace("import kotlinx.coroutines.launch", "import kotlinx.coroutines.launch\nimport kotlinx.serialization.json.Json")

old_load = """                    val domainPhotos = fetched.photos?.map {
                        com.sgbdevapps.space360.domain.model.IssuePhoto(
                            id = it.id,
                            issueId = issueId,
                            photoUrl = it.url,
                            uploadedAt = it.created_at
                        )
                    } ?: emptyList()
                    
                    _issue.value = Issue(
                        id = fetched.id,
                        title = fetched.title,
                        description = fetched.description ?: "",
                        status = fetched.status,
                        priority = fetched.priority ?: "Medium",
                        siteId = fetched.site_id ?: "",
                        assignedTo = "",
                        assignedToName = fetched.assigned_to ?: "Unassigned",
                        createdAt = fetched.created_at ?: "",
                        updatedAt = fetched.updated_at ?: "",
                        comments = domainComments,
                        photos = domainPhotos
                    )
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to load issue", e)"""

new_load = """                    val domainPhotos = fetched.photos?.map {
                        com.sgbdevapps.space360.domain.model.IssuePhoto(
                            id = it.id,
                            issueId = issueId,
                            photoUrl = it.url,
                            uploadedAt = it.created_at
                        )
                    }?.toMutableList() ?: mutableListOf()
                    
                    val finalComments = domainComments.toMutableList()
                    var finalStatus = fetched.status
                    
                    // Overlay offline actions
                    try {
                        val pendingActions = offlineSyncManager.getPendingItemsForResource("issue", issueId)
                        pendingActions.forEach { action ->
                            when (action.action) {
                                "update_status" -> {
                                    // payload is a string here, but in queueAction we encode it as JSON object sometimes
                                    // Actually, in updateIssueStatus we just queue the raw string: 
                                    // offlineSyncManager.queueAction("update_status", "issue", currentIssue.id, newStatus)
                                    // Wait, payload is a string.
                                    finalStatus = action.payload.replace("\"", "") // hacky unquote
                                }
                                "add_comment" -> {
                                    finalComments.add(
                                        com.sgbdevapps.space360.domain.model.IssueComment(
                                            id = "temp_${action.id}",
                                            issueId = issueId,
                                            userId = "current_user",
                                            userName = "You (Offline)",
                                            text = action.payload.replace("\"", ""),
                                            createdAt = "Pending Sync"
                                        )
                                    )
                                }
                                "upload_photo" -> {
                                    domainPhotos.add(
                                        com.sgbdevapps.space360.domain.model.IssuePhoto(
                                            id = "temp_${action.id}",
                                            issueId = issueId,
                                            photoUrl = action.payload.replace("\"", ""),
                                            uploadedAt = "Pending Sync"
                                        )
                                    )
                                }
                            }
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Failed to apply offline actions", e)
                    }
                    
                    _issue.value = Issue(
                        id = fetched.id,
                        title = fetched.title,
                        description = fetched.description ?: "",
                        status = finalStatus,
                        priority = fetched.priority ?: "Medium",
                        siteId = fetched.site_id ?: "",
                        assignedTo = "",
                        assignedToName = fetched.assigned_to ?: "Unassigned",
                        createdAt = fetched.created_at ?: "",
                        updatedAt = fetched.updated_at ?: "",
                        comments = finalComments,
                        photos = domainPhotos
                    )
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to load issue", e)"""
                    
if old_load in content:
    content = content.replace(old_load, new_load)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
