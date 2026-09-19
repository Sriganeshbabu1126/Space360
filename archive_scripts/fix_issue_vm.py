import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I will just insert them manually
new_stuff = """
    private val _sites = MutableStateFlow<List<Site>>(emptyList())
    val sites = _sites.asStateFlow()
    
    fun selectSite(siteId: String) {
        // Find the site or create a dummy one if sites aren't loaded here
        val site = _sites.value.find { it.id == siteId } 
                   ?: Site(id = siteId, name = "Project $siteId")
        _selectedSite.value = site
        loadIssues(siteId)
    }
"""

if "fun selectSite" not in content:
    content = content.replace("    val selectedSite = _selectedSite.asStateFlow()", "    val selectedSite = _selectedSite.asStateFlow()\n" + new_stuff)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done ViewModel")

# Now let's fix IssuesScreen.kt 
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
open_braces = 0
in_issues_screen = False

# I'll just rewrite IssuesScreen completely using Python, it's safer
