import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import javax.inject.Inject", "import javax.inject.Inject\nimport com.sgbdevapps.space360.domain.repository.SiteRepository")
content = content.replace("import com.sgbdevapps.space360.domain.repository.SiteRepository\n\n@HiltViewModel", "@HiltViewModel")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
