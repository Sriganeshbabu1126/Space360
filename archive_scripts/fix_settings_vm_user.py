import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/SettingsViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add UserManagementRepository to constructor
if "private val userManagementRepository: com.sgbdevapps.space360.data.repository.UserManagementRepository" not in content:
    old_const = """class SettingsViewModel @Inject constructor(
    private val userPreferences: UserPreferences,
    private val bluetoothManager: BluetoothManager"""
    new_const = """class SettingsViewModel @Inject constructor(
    private val userPreferences: UserPreferences,
    private val bluetoothManager: BluetoothManager,
    private val userManagementRepository: com.sgbdevapps.space360.data.repository.UserManagementRepository,
    private val authRepository: com.sgbdevapps.space360.data.repository.AuthRepository"""
    content = content.replace(old_const, new_const)

# Add currentUserRole and createNewUser
new_methods = """
    private val _currentUserRole = MutableStateFlow<String?>("Contractor") // default mocked
    val currentUserRole: StateFlow<String?> = _currentUserRole.asStateFlow()

    init {
        viewModelScope.launch {
            val user = authRepository.getCurrentUser().getOrNull()
            if (user != null) {
                _currentUserRole.value = user.role
            }
        }
        // ... (existing init content) ...
"""

# wait, better to find init { and replace
old_init = """    init {
        viewModelScope.launch {"""
new_init = """    private val _currentUserRole = MutableStateFlow<String?>("Contractor")
    val currentUserRole: StateFlow<String?> = _currentUserRole.asStateFlow()

    init {
        viewModelScope.launch {
            val user = authRepository.getCurrentUser().getOrNull()
            if (user != null) {
                _currentUserRole.value = user.role
            }
        }
        viewModelScope.launch {"""
content = content.replace(old_init, new_init)

end_methods = """
    fun createNewUser(name: String, email: String, role: String) {
        viewModelScope.launch {
            userManagementRepository.createNewUser(name, email, role)
        }
    }
}
"""
content = content.replace("}\n", "}\n" + end_methods)

# Wait, `}\n` might match multiple times. Let's just find the last brace.
idx = content.rfind("}")
if idx != -1:
    content = content[:idx] + """
    fun createNewUser(name: String, email: String, role: String) {
        viewModelScope.launch {
            userManagementRepository.createNewUser(name, email, role)
        }
    }
}
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
