import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Fix injection
old_inject = """@HiltViewModel
class IssueViewModel @Inject constructor(
    private val api: IssuesService,
    private val offlineSyncManager: OfflineSyncManager,
    private val siteRepository: SiteRepository
) : ViewModel() {"""
new_inject = """@HiltViewModel
class IssueViewModel @Inject constructor(
    private val api: IssuesService,
    private val offlineSyncManager: OfflineSyncManager,
    private val siteRepository: SiteRepository,
    private val sessionManager: SessionManager
) : ViewModel() {"""
if old_inject in content:
    content = content.replace(old_inject, new_inject)

# Replace init block
old_init = """    init {
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
    }"""
new_init = """    init {
        viewModelScope.launch {
            try {
                val result = siteRepository.getAssignedSites()
                if (result.isSuccess) {
                    _sites.value = result.getOrNull() ?: emptyList()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading sites", e)
            }
            
            sessionManager.selectedSite.collect { site ->
                _selectedSite.value = site
                site?.let { loadIssues(it.id) }
            }
        }
    }"""
if old_init in content:
    content = content.replace(old_init, new_init)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
