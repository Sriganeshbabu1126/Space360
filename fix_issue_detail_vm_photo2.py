import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add context to constructor
old_const = """class IssueDetailViewModel @Inject constructor(
    private val api: IssuesService,"""
new_const = """import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext

@dagger.hilt.android.lifecycle.HiltViewModel
class IssueDetailViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val api: IssuesService,"""
content = content.replace(old_const, new_const)

# Fix the addPhotoToIssue
old_upload = """                val contentResolver = getApplication<android.app.Application>().contentResolver
                val inputStream = contentResolver.openInputStream(photoUri)
                    ?: throw Exception("Cannot open image stream")

                val bytes = inputStream.readBytes()
                inputStream.close()

                val requestBody = okhttp3.RequestBody.create(okhttp3.MediaType.parse("image/jpeg"), bytes)
                val multipart = okhttp3.MultipartBody.Part.createFormData(
                    "photo", "photo_${System.currentTimeMillis()}.jpg", requestBody
                )

                // POST /api/issues/{issueId}/photos
                val apiService = com.sgbdevapps.space360.di.NetworkModule.provideRetrofit(
                    com.sgbdevapps.space360.di.NetworkModule.provideGson(),
                    com.sgbdevapps.space360.di.NetworkModule.provideOkHttpClient(
                        com.sgbdevapps.space360.di.NetworkModule.provideAuthInterceptor(getApplication<android.app.Application>()),
                        com.sgbdevapps.space360.di.NetworkModule.provideLoggingInterceptor()
                    )
                ).create(com.sgbdevapps.space360.data.remote.IssuesService::class.java)

                apiService.uploadIssuePhoto(issueId, multipart)"""
new_upload = """                val contentResolver = context.contentResolver
                val inputStream = contentResolver.openInputStream(photoUri)
                    ?: throw Exception("Cannot open image stream")

                val bytes = inputStream.readBytes()
                inputStream.close()

                val requestBody = okhttp3.RequestBody.create(okhttp3.MediaType.parse("image/jpeg"), bytes)
                val multipart = okhttp3.MultipartBody.Part.createFormData(
                    "photo", "photo_${System.currentTimeMillis()}.jpg", requestBody
                )

                api.uploadIssuePhoto(issueId, multipart)"""
content = content.replace(old_upload, new_upload)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
