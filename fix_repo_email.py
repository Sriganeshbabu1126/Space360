import os

filepath = "app/src/main/java/com/sgbdevapps/space360/data/repository/UserManagementRepository.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add apiService to constructor
old_const = """class UserManagementRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {"""
new_const = """class UserManagementRepository @Inject constructor(
    @ApplicationContext private val context: Context,
    private val apiService: com.sgbdevapps.space360.data.remote.AuthService
) {"""
content = content.replace(old_const, new_const)

# Add the email logic after writeUserToSheet
old_write = """            writeUserToSheet(
                uid = uid,
                name = name,
                email = email,
                role = role,
                password = DUMMY_PASSWORD,
                status = "MUST_CHANGE_PASSWORD"
            )

            Timber.i("New user created: $email (uid=$uid)")"""
new_write = """            writeUserToSheet(
                uid = uid,
                name = name,
                email = email,
                role = role,
                password = DUMMY_PASSWORD,
                status = "MUST_CHANGE_PASSWORD"
            )
            
            try {
                apiService.notifyNewUser(com.sgbdevapps.space360.data.remote.NotifyUserRequest(
                    name = name,
                    email = email,
                    temp_password = DUMMY_PASSWORD
                ))
                Timber.i("Welcome email sent to $email")
            } catch (e: Exception) {
                Timber.w("Welcome email failed — user still created: ${e.message}")
            }

            Timber.i("New user created: $email (uid=$uid)")"""
content = content.replace(old_write, new_write)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
