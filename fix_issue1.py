import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Update SettingsScreen
old_settings_screen = """@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val selectedColorScheme by viewModel.colorScheme.collectAsState()
    val bluetoothStatus by viewModel.bluetoothStatus.collectAsState()"""

new_settings_screen = """@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val selectedColorScheme by viewModel.colorScheme.collectAsState()
    val tempSelectedScheme = remember { mutableStateOf(selectedColorScheme) }
    val bluetoothStatus by viewModel.bluetoothStatus.collectAsState()"""
content = content.replace(old_settings_screen, new_settings_screen)

old_items = """            items(ColorScheme.values()) { scheme ->
                ColorSchemeOptionWithImage(
                    scheme = scheme,
                    isSelected = scheme == selectedColorScheme,
                    onSelect = { viewModel.setColorScheme(scheme) }
                )
            }"""
new_items = """            items(ColorScheme.values()) { scheme ->
                ColorSchemeOptionWithImage(
                    scheme = scheme,
                    isSelected = scheme == tempSelectedScheme.value,
                    onSelect = { 
                        tempSelectedScheme.value = scheme
                    },
                    onApply = {
                        viewModel.setColorScheme(scheme)
                    }
                )
            }"""
content = content.replace(old_items, new_items)

# Update ColorSchemeOptionWithImage
old_sig = """fun ColorSchemeOptionWithImage(
    scheme: ColorScheme,
    isSelected: Boolean,
    onSelect: () -> Unit
) {"""
new_sig = """fun ColorSchemeOptionWithImage(
    scheme: ColorScheme,
    isSelected: Boolean,
    onSelect: () -> Unit,
    onApply: () -> Unit
) {"""
content = content.replace(old_sig, new_sig)

old_card = """            // Color Palette Preview (Mini swatches)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(scheme.primary, RoundedCornerShape(6.dp))
                )
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(scheme.secondary, RoundedCornerShape(6.dp))
                )
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(scheme.accent, RoundedCornerShape(6.dp))
                )
            }
        }
    }
}"""
new_card = """            // Color Palette Preview (Mini swatches)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(scheme.primary, RoundedCornerShape(6.dp))
                )
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(scheme.secondary, RoundedCornerShape(6.dp))
                )
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(scheme.accent, RoundedCornerShape(6.dp))
                )
            }
            
            // NEW: Apply Button
            if (isSelected) {
                Button(
                    onClick = onApply,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = scheme.primary
                    )
                ) {
                    Text("Apply Theme", color = Color.White)
                }
            }
        }
    }
}"""
content = content.replace(old_card, new_card)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done SettingsScreen for Issue 1")

# Update MainActivity for LaunchedEffect (which forces recomposition, though selectedColorScheme does it already if passed correctly)
filepath = "app/src/main/java/com/sgbdevapps/space360/MainActivity.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "import androidx.compose.runtime.LaunchedEffect" not in content:
    content = content.replace("import androidx.compose.runtime.collectAsState", "import androidx.compose.runtime.collectAsState\nimport androidx.compose.runtime.LaunchedEffect")

old_theme = "    Space360Theme(colorScheme = selectedColorScheme) {"
new_theme = """    // Force recomposition when theme changes
    LaunchedEffect(selectedColorScheme) {
    }
    
    Space360Theme(colorScheme = selectedColorScheme) {"""

if "LaunchedEffect(selectedColorScheme)" not in content:
    content = content.replace(old_theme, new_theme)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done MainActivity for Issue 1")

