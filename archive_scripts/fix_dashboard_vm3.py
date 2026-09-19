import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/DashboardViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import com.sgbdevapps.space360.domain.SessionManager" not in content:
    content = content.replace("import com.sgbdevapps.space360.domain.repository.SiteRepository", "import com.sgbdevapps.space360.domain.repository.SiteRepository\nimport com.sgbdevapps.space360.domain.SessionManager")

old_inject = """class DashboardViewModel @Inject constructor(
    private val siteRepository: SiteRepository,
    private val issueRepository: IssueRepository
) : ViewModel() {"""
new_inject = """class DashboardViewModel @Inject constructor(
    private val siteRepository: SiteRepository,
    private val issueRepository: IssueRepository,
    private val sessionManager: SessionManager
) : ViewModel() {"""
if old_inject in content:
    content = content.replace(old_inject, new_inject)

old_select = """    fun selectSite(siteId: String) {
        _selectedSite.value = _sites.value.find { it.id == siteId }
    }"""
new_select = """    fun selectSite(siteId: String) {
        val site = _sites.value.find { it.id == siteId }
        _selectedSite.value = site
        sessionManager.setSelectedSite(site)
    }"""
if old_select in content:
    content = content.replace(old_select, new_select)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
