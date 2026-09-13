import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiService.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_upload_method = """    @retrofit2.http.Multipart
    @POST("issues/{issueId}/photos")
    suspend fun uploadIssuePhoto(
        @Path("issueId") issueId: String,
        @retrofit2.http.Part photo: okhttp3.MultipartBody.Part
    ): retrofit2.Response<Unit>
}"""
content = content.replace("    suspend fun createIssue(@Body request: CreateIssueRequest): IssueResponse\n}", "    suspend fun createIssue(@Body request: CreateIssueRequest): IssueResponse\n\n" + new_upload_method)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

vm_filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(vm_filepath, "r", encoding="utf-8") as f:
    vm_content = f.read()

vm_content = vm_content.replace(
    'okhttp3.MediaType.Companion.toMediaTypeOrNull("image/jpeg")!!', 
    'okhttp3.MediaType.parse("image/jpeg")'
)

with open(vm_filepath, "w", encoding="utf-8") as f:
    f.write(vm_content)
    
print("Done")
