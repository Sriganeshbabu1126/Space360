import os
import re

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add ExitToApp icon
if "import androidx.compose.material.icons.filled.ExitToApp" not in content:
    content = content.replace("import androidx.compose.material.icons.filled.Bluetooth", "import androidx.compose.material.icons.filled.Bluetooth\nimport androidx.compose.material.icons.filled.ExitToApp\nimport com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel")

old_sig = """fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel()
) {"""
new_sig = """fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel(),
    authViewModel: AuthViewModel = hiltViewModel()
) {"""
content = content.replace(old_sig, new_sig)

old_col = """            Text(
                "c 2026 Space360. All rights reserved.",
                style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray)
            )
        }
    }
}"""
new_col = """            Text(
                "c 2026 Space360. All rights reserved.",
                style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray)
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Button(
                onClick = { authViewModel.logout() },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
            ) {
                Icon(Icons.Filled.ExitToApp, contentDescription = "Logout")
                Spacer(modifier = Modifier.width(8.dp))
                Text("Log Out")
            }
        }
    }
}"""
content = content.replace(old_col, new_col)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
