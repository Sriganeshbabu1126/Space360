import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

init_block = """
    init {
        viewModelScope.launch {
            try {
                // Fetch user sites when viewmodel is created
                val result = siteRepository.getAssignedSites()
                if (result.isSuccess) {
                    _sites.value = result.getOrNull() ?: emptyList()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading sites", e)
            }
        }
    }
"""

if "siteRepository.getAssignedSites()" not in content:
    # Need to make sure siteRepository is injected
    if "private val siteRepository: SiteRepository" not in content:
        content = content.replace(
            "class IssueViewModel @Inject constructor(\n    private val api: IssuesService,\n    private val offlineSyncManager: OfflineSyncManager\n)",
            "import com.sgbdevapps.space360.domain.repository.SiteRepository\nclass IssueViewModel @Inject constructor(\n    private val api: IssuesService,\n    private val offlineSyncManager: OfflineSyncManager,\n    private val siteRepository: SiteRepository\n)"
        )
    
    # insert init block right after TAG
    content = content.replace('private val TAG = "IssueViewModel"', 'private val TAG = "IssueViewModel"\n' + init_block)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done IssueViewModel init")
