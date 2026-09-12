import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_method = """
    fun updateIssueStatus(newStatus: String) {
        val currentIssue = _issue.value ?: return
        // Update local state optimistically
        _issue.value = currentIssue.copy(status = newStatus)
        // Note: For full implementation we should call the API:
        // viewModelScope.launch { api.updateIssueStatus(...) }
    }
"""

if "fun updateIssueStatus" not in content:
    content = content.replace("    fun loadIssue(issueId: String)", new_method + "\n    fun loadIssue(issueId: String)")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
