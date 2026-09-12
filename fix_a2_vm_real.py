import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# The previous replacement failed to parse correctly, or I need to rewrite the map section
# Let's replace the whole loadIssue block
import re

# I will just find `fun loadIssue` and replace everything inside it

old_load_issue = """    fun loadIssue(issueId: String) {
        currentIssueId = issueId
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                // Since this is MVP Phase 4a, we call the backend
                val fetched = api.getIssueById(issueId)
                _issue.value = Issue(
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
                }
            } catch (e: Exception) {
                Log.e(TAG, "Failed to load issue", e)
                _error.value = "Could not load issue"
            } finally {
                _isLoading.value = false
            }
        }
    }"""

new_load_issue = """    fun loadIssue(issueId: String) {
        currentIssueId = issueId
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                val fetched = api.getIssueById(issueId)
                
                val domainComments = fetched.comments?.map { 
                    com.sgbdevapps.space360.domain.model.IssueComment(
                        id = it.id,
                        text = it.text,
                        authorName = it.user_name,
                        createdAt = it.created_at
                    )
                } ?: emptyList()
                
                val domainPhotos = fetched.photos?.map {
                    com.sgbdevapps.space360.domain.model.IssuePhoto(
                        id = it.id,
                        url = it.file_url,
                        createdAt = it.created_at
                    )
                } ?: emptyList()
                
                _issue.value = Issue(
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
                    comments = domainComments,
                    photos = domainPhotos
                )
            } catch (e: Exception) {
                Log.e(TAG, "Failed to load issue", e)
                _error.value = "Could not load issue"
            } finally {
                _isLoading.value = false
            }
        }
    }"""

if old_load_issue in content:
    content = content.replace(old_load_issue, new_load_issue)
else:
    # try regex just in case
    pattern = re.compile(r"    fun loadIssue\(issueId: String\) \{.*?(?=    fun uploadPhotoBitmap)", re.DOTALL)
    content = re.sub(pattern, new_load_issue + "\n    ", content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a2 vm real")
