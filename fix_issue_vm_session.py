import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import com.sgbdevapps.space360.domain.SessionManager" not in content:
    content = content.replace("import com.sgbdevapps.space360.domain.repository.SiteRepository", "import com.sgbdevapps.space360.domain.repository.SiteRepository\nimport com.sgbdevapps.space360.domain.SessionManager")

old_inject = """class IssueViewModel @Inject constructor(
    private val issueRepository: IssueRepository,
    private val siteRepository: SiteRepository
) : ViewModel() {"""
new_inject = """class IssueViewModel @Inject constructor(
    private val issueRepository: IssueRepository,
    private val siteRepository: SiteRepository,
    private val sessionManager: SessionManager
) : ViewModel() {"""
if old_inject in content:
    content = content.replace(old_inject, new_inject)

old_load = """    fun loadIssues(siteId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            // If siteId is "all", we just get everything for now
            val result = if (siteId == "all" || siteId.isEmpty()) {
                issueRepository.getIssuesBySite(null)
            } else {
                issueRepository.getIssuesBySite(siteId)
            }
            
            if (result.isSuccess) {
                _issues.value = result.getOrNull() ?: emptyList()
            } else {
                _error.value = result.exceptionOrNull()?.message ?: "Failed to load issues"
            }
            _isLoading.value = false
        }
    }"""
new_load = """    init {
        viewModelScope.launch {
            sessionManager.selectedSite.collect { site ->
                _selectedProject.value = site
                site?.let { loadIssues(it.id) }
            }
        }
    }

    fun loadIssues(siteId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            val result = issueRepository.getIssuesBySite(siteId)
            
            if (result.isSuccess) {
                _issues.value = result.getOrNull() ?: emptyList()
            } else {
                _error.value = result.exceptionOrNull()?.message ?: "Failed to load issues"
            }
            _isLoading.value = false
        }
    }"""
if old_load in content:
    content = content.replace(old_load, new_load)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
