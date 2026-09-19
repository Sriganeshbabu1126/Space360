import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('offlineSyncManager.queueAction("update_status", "issue", currentIssue.id, newStatus)', 'offlineSyncManager.queueAction("update_status", "issue", currentIssue.id, UpdateIssueStatusRequest(newStatus))')

content = content.replace('offlineSyncManager.queueAction("add_comment", "issue", issueId, text)', 'offlineSyncManager.queueAction("add_comment", "issue", issueId, AddCommentRequest(text))')

# Update overlay parsing in loadIssue
old_parse = """                            when (action.action) {
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
                                }"""
new_parse = """                            when (action.action) {
                                "update_status" -> {
                                    try {
                                        val req = Json.decodeFromString<UpdateIssueStatusRequest>(action.payload)
                                        finalStatus = req.status
                                    } catch (e: Exception) {}
                                }
                                "add_comment" -> {
                                    try {
                                        val req = Json.decodeFromString<AddCommentRequest>(action.payload)
                                        finalComments.add(
                                            com.sgbdevapps.space360.domain.model.IssueComment(
                                                id = "temp_${action.id}",
                                                issueId = issueId,
                                                userId = "current_user",
                                                userName = "You (Offline)",
                                                text = req.text,
                                                createdAt = "Pending Sync"
                                            )
                                        )
                                    } catch(e: Exception) {}
                                }"""
if old_parse in content:
    content = content.replace(old_parse, new_parse)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
