import os
import re

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/SettingsScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add necessary imports
if "import androidx.compose.foundation.shape.CircleShape" not in content:
    content = content.replace("import androidx.compose.foundation.shape.RoundedCornerShape", "import androidx.compose.foundation.shape.RoundedCornerShape\nimport androidx.compose.foundation.shape.CircleShape")
if "import com.sgbdevapps.space360.presentation.viewmodels.BluetoothStatus" not in content:
    content = content.replace("import com.sgbdevapps.space360.presentation.viewmodels.SettingsViewModel", "import com.sgbdevapps.space360.presentation.viewmodels.SettingsViewModel\nimport com.sgbdevapps.space360.presentation.viewmodels.BluetoothStatus")
if "import androidx.compose.material.icons.filled.Bluetooth" not in content:
    content = content.replace("import androidx.compose.material3.*", "import androidx.compose.material3.*\nimport androidx.compose.material.icons.filled.Bluetooth")
if "import androidx.compose.material3.ListItem" not in content:
    content = content.replace("import androidx.compose.material3.*", "import androidx.compose.material3.*\nimport androidx.compose.material3.ListItem")

# Replace BluetoothConnectionCard
old_card_pattern = r"@Composable\s+fun BluetoothConnectionCard.*?\}  // End BluetoothConnectionCard"
# But we might not have a comment. Let's just find the start of BluetoothConnectionCard and replace everything up to the next @Composable or EOF.

parts = content.split("@Composable\nfun BluetoothConnectionCard(")
before = parts[0]
after_card = parts[1].split("@Composable\nfun AboutCard()")[1]

new_card = """@Composable
fun BluetoothConnectionCard(
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val bluetoothStatus by viewModel.bluetoothStatus.collectAsState()
    val availableDevices by viewModel.availableDevices.collectAsState()
    val isSearching by viewModel.isSearching.collectAsState()
    var showDeviceList by remember { mutableStateOf(false) }
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp, 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        "Insta360 X4",
                        style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Bold)
                    )
                    Text(
                        when (bluetoothStatus) {
                            is BluetoothStatus.CONNECTED -> 
                                "Connected: ${(bluetoothStatus as BluetoothStatus.CONNECTED).deviceName}"
                            BluetoothStatus.DISCONNECTED -> 
                                "Not connected"
                            BluetoothStatus.SEARCHING -> 
                                "Searching..."
                            BluetoothStatus.ERROR -> 
                                "Connection error"
                        },
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = when (bluetoothStatus) {
                                is BluetoothStatus.CONNECTED -> Color(0xFF4CAF50)
                                else -> Color.Gray
                            }
                        )
                    )
                }
                
                // Status indicator
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .background(
                            color = when (bluetoothStatus) {
                                is BluetoothStatus.CONNECTED -> Color(0xFF4CAF50)
                                BluetoothStatus.SEARCHING -> Color(0xFFFFC107)
                                else -> Color.Gray
                            },
                            shape = CircleShape
                        )
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Search/Connect Button
            Button(
                onClick = {
                    if (bluetoothStatus is BluetoothStatus.CONNECTED) {
                        viewModel.disconnectBluetooth()
                    } else {
                        viewModel.initiateBluetooth()
                        showDeviceList = true
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isSearching
            ) {
                Icon(
                    Icons.Filled.Bluetooth,
                    contentDescription = "Bluetooth"
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    if (bluetoothStatus is BluetoothStatus.CONNECTED) "Disconnect" 
                    else "Search & Connect"
                )
            }
            
            // Device List
            if (showDeviceList && availableDevices.isNotEmpty()) {
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    "Available Devices:",
                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Bold)
                )
                
                availableDevices.forEach { device ->
                    ListItem(
                        headlineContent = { Text(device.name ?: "Unknown") },
                        supportingContent = { Text(device.address) },
                        modifier = Modifier.clickable {
                            viewModel.connectDevice(device)
                            showDeviceList = false
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun AboutCard()"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(before + new_card + after_card)
print("Done Bluetooth card")

