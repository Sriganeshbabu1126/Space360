import os

# 1. Fix SettingsViewModel
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/SettingsViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("userPreferences.colorSchemeFlow", "userPreferences.selectedColorScheme")
content = content.replace("ColorScheme.DEFAULT", "ColorScheme.SUNSET")
content = content.replace("userPreferences.setColorScheme(scheme.name)", "userPreferences.setColorScheme(scheme)")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# 2. Fix SettingsScreen.kt
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I also noticed earlier: "Cannot infer type for this parameter" on line 41/42. 
# val tempSelectedScheme = remember { mutableStateOf(selectedColorScheme) }
# We need to make sure type is inferred or explicitly stated.
# val tempSelectedScheme = remember(selectedColorScheme) { mutableStateOf(selectedColorScheme) }

old_temp = "val tempSelectedScheme = remember { mutableStateOf(selectedColorScheme) }"
new_temp = "val tempSelectedScheme = remember(selectedColorScheme) { mutableStateOf(selectedColorScheme) }"
content = content.replace(old_temp, new_temp)

old_bt_call = """                BluetoothConnectionCard(
                    status = bluetoothStatus,
                    onConnect = { viewModel.initiateBluetooth() }
                )"""
new_bt_call = """                BluetoothConnectionCard(viewModel = viewModel)"""
content = content.replace(old_bt_call, new_bt_call)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
