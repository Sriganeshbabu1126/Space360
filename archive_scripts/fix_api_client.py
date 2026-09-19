import os

api_models = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiModels.kt"
with open(api_models, "r", encoding="utf-8") as f:
    models_content = f.read()
if "data class NotifyUserRequest" not in models_content:
    models_content += """
data class NotifyUserRequest(
    val name: String,
    val email: String,
    val temp_password: String
)
"""
    with open(api_models, "w", encoding="utf-8") as f:
        f.write(models_content)

api_service = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiService.kt"
with open(api_service, "r", encoding="utf-8") as f:
    service_content = f.read()

old_auth = """interface AuthService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse
}"""
new_auth = """interface AuthService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse
    
    @POST("admin/notify-new-user")
    suspend fun notifyNewUser(@Body request: NotifyUserRequest): retrofit2.Response<Unit>
}"""
if old_auth in service_content:
    service_content = service_content.replace(old_auth, new_auth)
    with open(api_service, "w", encoding="utf-8") as f:
        f.write(service_content)

print("Done")
