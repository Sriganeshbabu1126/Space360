import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/PathCaptureViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import com.sgbdevapps.space360.domain.SessionManager" not in content:
    content = content.replace("import com.sgbdevapps.space360.domain.repository.AuthRepository", "import com.sgbdevapps.space360.domain.repository.AuthRepository\nimport com.sgbdevapps.space360.domain.SessionManager")

old_inject = """class PathCaptureViewModel @Inject constructor(
    application: Application,
    private val pathRepository: PathRepository,
    private val authRepository: AuthRepository
) : AndroidViewModel(application) {"""
new_inject = """class PathCaptureViewModel @Inject constructor(
    application: Application,
    private val pathRepository: PathRepository,
    private val authRepository: AuthRepository,
    private val sessionManager: SessionManager
) : AndroidViewModel(application) {"""
if old_inject in content:
    content = content.replace(old_inject, new_inject)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
