import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("@HiltViewModel\nimport com.sgbdevapps.space360.domain.repository.SiteRepository\nclass IssueViewModel", "import com.sgbdevapps.space360.domain.repository.SiteRepository\n\n@HiltViewModel\nclass IssueViewModel")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
