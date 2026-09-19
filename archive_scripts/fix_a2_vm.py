import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I mapped comments to emptyList() previously:
old_map = """_issue.value = Issue(id = fetched.id, title = fetched.title, description = fetched.description ?: "", status = fetched.status, priority = fetched.priority ?: "", siteId = fetched.site_id, assignedTo = "", assignedToName = "", createdAt = "", updatedAt = "", comments = emptyList(), photos = emptyList())"""
new_map = """_issue.value = Issue(
                    id = fetched.id, 
                    title = fetched.title, 
                    description = fetched.description ?: "", 
                    status = fetched.status, 
                    priority = fetched.priority ?: "", 
                    siteId = fetched.site_id, 
                    assignedTo = "", 
                    assignedToName = "", 
                    createdAt = "", 
                    updatedAt = "", 
                    comments = emptyList(), // Fallback for MVP, we'll fetch actual comments below
                    photos = emptyList()
                )
                // Actually fetch comments since API might separate them
                try {
                    val comments = api.getIssueComments(issueId)
                    val issuePhotos = emptyList<com.sgbdevapps.space360.domain.model.IssuePhoto>() // mock
                    
                    val domainComments = comments.map { 
                        com.sgbdevapps.space360.domain.model.IssueComment(
                            id = it.id,
                            text = it.text,
                            authorName = it.author_name,
                            createdAt = it.created_at
                        )
                    }
                    _issue.value = _issue.value?.copy(comments = domainComments, photos = issuePhotos)
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to load comments", e)
                }"""
content = content.replace(old_map, new_map)

# Let's fix addComment to immediately reload
old_add_comment = """    fun addComment(text: String) {
        val issueId = currentIssueId ?: return
        viewModelScope.launch {
            try {
                api.addComment(issueId, AddCommentRequest(text))
                // Reload
                loadIssue(issueId)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to add comment", e)
                offlineSyncManager.queueAction("add_comment", "issue", issueId, AddCommentRequest(text))
            }
        }
    }"""
new_add_comment = """    fun addComment(text: String) {
        val issueId = currentIssueId ?: return
        viewModelScope.launch {
            try {
                api.addComment(issueId, AddCommentRequest(text))
                // Reload immediately
                loadIssue(issueId)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to add comment", e)
                offlineSyncManager.queueAction("add_comment", "issue", issueId, text)
                
                // Optimistic UI update
                val current = _issue.value ?: return@launch
                val newComments = current.comments.toMutableList()
                newComments.add(
                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = "temp_${System.currentTimeMillis()}",
                        text = text,
                        authorName = "You (Offline)",
                        createdAt = "Just now"
                    )
                )
                _issue.value = current.copy(comments = newComments)
            }
        }
    }"""
content = content.replace(old_add_comment, new_add_comment)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a2 vm")
