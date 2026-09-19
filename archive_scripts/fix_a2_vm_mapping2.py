import os
import re

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I want comments to use it.created_at
content = content.replace("createdAt = it.uploaded_at ?: \"\"", "createdAt = it.created_at", 1) # First occurrence is comments
# Actually, the first occurrence was comments, which was `createdAt = it.created_at`, I replaced it.
# Let's just restore the whole loadIssue explicitly to be safe.

old_load_issue = """    fun loadIssue(issueId: String) {
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
                        createdAt = it.uploaded_at ?: ""
                    )
                } ?: emptyList()
                
                val domainPhotos = fetched.photos?.map {
                    com.sgbdevapps.space360.domain.model.IssuePhoto(
                        id = it.id,
                        url = it.photo_url,
                        createdAt = it.uploaded_at ?: ""
                    )
                } ?: emptyList()"""

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
                        url = it.photo_url,
                        createdAt = it.uploaded_at ?: ""
                    )
                } ?: emptyList()"""

content = content.replace(old_load_issue, new_load_issue)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done mapping fix 2")
