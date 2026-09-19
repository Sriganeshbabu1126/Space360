import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/remote/ApiService.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_auth = """interface AuthService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    @POST("admin/notify-new-user")
    suspend fun notifyNewUser(@Body request: com.sgbdevapps.space360.data.remote.NotifyUserRequest): retrofit2.Response<Unit>
"""
content = content.replace("""interface AuthService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse
""", new_auth)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
