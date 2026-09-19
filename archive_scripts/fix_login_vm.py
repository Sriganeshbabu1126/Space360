import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/AuthViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add mustChangePassword flow
if "private val _mustChangePassword" not in content:
    old_state = """    private val _loginError = MutableStateFlow<String?>(null)
    val loginError: StateFlow<String?> = _loginError.asStateFlow()"""
    new_state = """    private val _loginError = MutableStateFlow<String?>(null)
    val loginError: StateFlow<String?> = _loginError.asStateFlow()
    
    private val _mustChangePassword = MutableStateFlow(false)
    val mustChangePassword: StateFlow<Boolean> = _mustChangePassword.asStateFlow()"""
    content = content.replace(old_state, new_state)

# Replace login block
# It might be in AuthViewModel.kt or LoginViewModel.kt
# We'll use regex or simple replace
old_login = """            try {
                _isLoading.value = true
                val result = authRepository.login(email, password)
                if (result.isSuccess) {
                    _loginSuccess.value = true
                } else {
                    _loginError.value = result.exceptionOrNull()?.message ?: "Login failed"
                }
            } catch (e: Exception) {
                _loginError.value = e.message ?: "An unexpected error occurred"
            }"""
new_login = """            try {
                _isLoading.value = true
                val result = authRepository.login(email, password)
                if (result.isSuccess) {
                    if (password == "welcomespace360") {
                        _mustChangePassword.value = true
                    } else {
                        _loginSuccess.value = true
                    }
                } else {
                    _loginError.value = result.exceptionOrNull()?.message ?: "Login failed"
                }
            } catch (e: Exception) {
                _loginError.value = e.message ?: "An unexpected error occurred"
            }"""
content = content.replace(old_login, new_login)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
