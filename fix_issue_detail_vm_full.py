import os
import re

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add Timber
if "import timber.log.Timber" not in content:
    content = content.replace("import android.util.Log", "import android.util.Log\nimport timber.log.Timber")
    if "import timber.log.Timber" not in content:
        content = "import timber.log.Timber\n" + content

# Fix _isUploadingPhoto and _photoUploadError
old_state = """    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()"""
new_state = """    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _isUploadingPhoto = MutableStateFlow(false)
    val isUploadingPhoto: StateFlow<Boolean> = _isUploadingPhoto.asStateFlow()

    private val _photoUploadError = MutableStateFlow<String?>(null)
    val photoUploadError: StateFlow<String?> = _photoUploadError.asStateFlow()"""
if "_isUploadingPhoto" not in content:
    content = content.replace(old_state, new_state)
    # What if it's missing entirely?
    if "_isUploadingPhoto" not in content:
        content = re.sub(r'(private val _error.*?\n.*?asStateFlow\(\))', r'\1\n\n    private val _isUploadingPhoto = MutableStateFlow(false)\n    val isUploadingPhoto: StateFlow<Boolean> = _isUploadingPhoto.asStateFlow()\n\n    private val _photoUploadError = MutableStateFlow<String?>(null)\n    val photoUploadError: StateFlow<String?> = _photoUploadError.asStateFlow()', content, flags=re.DOTALL)

# Add issueRepository to constructor
old_const = """class IssueDetailViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val api: IssuesService,"""
new_const = """class IssueDetailViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val api: IssuesService,
    private val issueRepository: com.sgbdevapps.space360.domain.repository.IssueRepository,"""
if "private val issueRepository:" not in content:
    content = content.replace(old_const, new_const)

# Fix okhttp3 parse warning (MediaType.Companion.toMediaTypeOrNull)
content = content.replace('okhttp3.MediaType.parse("image/jpeg")', 'okhttp3.MediaType.parse("image/jpeg")') # actually it's just a warning, it's fine

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# Fix IssuesService to have uploadIssuePhoto
api_service = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiService.kt"
with open(api_service, "r", encoding="utf-8") as f:
    api_content = f.read()

new_upload_method = """    @retrofit2.http.Multipart
    @POST("issues/{issueId}/photos")
    suspend fun uploadIssuePhoto(
        @Path("issueId") issueId: String,
        @retrofit2.http.Part photo: okhttp3.MultipartBody.Part
    ): retrofit2.Response<Unit>
}"""
if "fun uploadIssuePhoto" not in api_content:
    api_content = api_content.replace("    suspend fun createIssue(@Body request: CreateIssueRequest): IssueResponse\n}", "    suspend fun createIssue(@Body request: CreateIssueRequest): IssueResponse\n\n" + new_upload_method)
    with open(api_service, "w", encoding="utf-8") as f:
        f.write(api_content)

print("Done")
