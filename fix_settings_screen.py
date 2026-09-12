import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I don't see navController passed to SettingsScreen in NavGraph. Wait, NavGraph calls `SettingsScreen()`.
# Let's add onLogout to SettingsScreen.
old_sig = """fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel(),
    authViewModel: AuthViewModel = hiltViewModel()
) {"""
new_sig = """fun SettingsScreen(
    onLogout: () -> Unit = {},
    viewModel: SettingsViewModel = hiltViewModel(),
    authViewModel: AuthViewModel = hiltViewModel()
) {"""
content = content.replace(old_sig, new_sig)

old_btn = """            Button(
                onClick = { authViewModel.logout() },"""
new_btn = """            Button(
                onClick = { 
                    authViewModel.logout()
                    onLogout()
                },"""
content = content.replace(old_btn, new_btn)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
