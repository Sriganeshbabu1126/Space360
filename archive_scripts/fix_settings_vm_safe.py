import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/SettingsViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add imports
imports = """import androidx.lifecycle.ViewModel
import com.sgbdevapps.space360.data.repository.UserManagementRepository
import com.sgbdevapps.space360.domain.repository.AuthRepository"""
content = content.replace("import androidx.lifecycle.ViewModel", imports)

# Update constructor
old_const = """class SettingsViewModel @Inject constructor(
    private val userPreferences: UserPreferences,
    private val bluetoothManager: BluetoothManager
) : ViewModel() {"""
new_const = """class SettingsViewModel @Inject constructor(
    private val userPreferences: UserPreferences,
    private val bluetoothManager: BluetoothManager,
    private val userManagementRepository: UserManagementRepository,
    private val authRepository: AuthRepository
) : ViewModel() {"""
content = content.replace(old_const, new_const)

# Update init block to also get role
old_init = """    init {
        viewModelScope.launch {
            userPreferences.selectedColorScheme.collect { schemeName ->"""
new_init = """    private val _currentUserRole = MutableStateFlow<String?>("Contractor")
    val currentUserRole: StateFlow<String?> = _currentUserRole.asStateFlow()

    init {
        viewModelScope.launch {
            val user = authRepository.getCurrentUser().getOrNull()
            if (user != null) {
                _currentUserRole.value = user.role
            }
        }
        viewModelScope.launch {
            userPreferences.selectedColorScheme.collect { schemeName ->"""
content = content.replace(old_init, new_init)

# Add createNewUser at the bottom
new_func = """
    fun disconnectBluetooth() {
        bluetoothManager.disconnect()
        _bluetoothStatus.value = BluetoothStatus.DISCONNECTED
    }

    fun createNewUser(name: String, email: String, role: String) {
        viewModelScope.launch {
            userManagementRepository.createNewUser(name, email, role)
        }
    }
}"""
content = content.replace("""    fun disconnectBluetooth() {
        bluetoothManager.disconnect()
        _bluetoothStatus.value = BluetoothStatus.DISCONNECTED
    }
}""", new_func)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
