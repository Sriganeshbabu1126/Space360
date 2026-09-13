import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/AuthViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_login = """    fun login(email: String, password: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.login(email, password)
            if (result.isSuccess) {
                val user = result.getOrNull()!!; com.sgbdevapps.space360.utils.CrashlyticsHelper.setUserContext(userId = user.id, email = user.email); _isLoggedIn.value = true
                _authState.value = AuthState.Success(result.getOrNull()!!)
            } else {
                _authState.value = AuthState.Error(result.exceptionOrNull()?.message ?: "Login failed")
            }
        }
    }"""
new_login = """    private val _mustChangePassword = MutableStateFlow(false)
    val mustChangePassword: StateFlow<Boolean> = _mustChangePassword

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.login(email, password)
            if (result.isSuccess) {
                val user = result.getOrNull()!!
                com.sgbdevapps.space360.utils.CrashlyticsHelper.setUserContext(userId = user.id, email = user.email)
                
                if (password == "welcomespace360") {
                    _mustChangePassword.value = true
                } else {
                    _isLoggedIn.value = true
                    _authState.value = AuthState.Success(user)
                }
            } else {
                _authState.value = AuthState.Error(result.exceptionOrNull()?.message ?: "Login failed")
            }
        }
    }"""
if old_login in content:
    content = content.replace(old_login, new_login)
else:
    print("Failed to replace login method")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
