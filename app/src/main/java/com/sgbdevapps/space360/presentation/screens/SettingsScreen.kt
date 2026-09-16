package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bluetooth
import androidx.compose.material.icons.filled.ExitToApp
import com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.material3.ListItem
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.sgbdevapps.space360.data.model.ColorScheme
import com.sgbdevapps.space360.presentation.viewmodels.SettingsViewModel
import com.sgbdevapps.space360.presentation.viewmodels.BluetoothStatus

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onLogout: () -> Unit = {},
    viewModel: SettingsViewModel = hiltViewModel(),
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val selectedColorScheme by viewModel.colorScheme.collectAsState()
    val tempSelectedScheme = remember(selectedColorScheme) { mutableStateOf(selectedColorScheme) }
    val bluetoothStatus by viewModel.bluetoothStatus.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings") }
            )
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Color Scheme Section
            item {
                Text(
                    "Theme",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(16.dp, 8.dp)
                )
                Text(
                    "Select your preferred color scheme",
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = Color.Gray
                    ),
                    modifier = Modifier.padding(horizontal = 16.dp)
                )
            }
            
            items(ColorScheme.values()) { scheme ->
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
            }
            
            item { HorizontalDivider(modifier = Modifier.padding(vertical = 16.dp)) }
            
            // Bluetooth Section
            item {
                Text(
                    "Bluetooth",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(16.dp, 8.dp)
                )
            }
            
            item {
                BluetoothConnectionCard(viewModel = viewModel)
            }
            
            item { HorizontalDivider(modifier = Modifier.padding(vertical = 16.dp)) }
            
            // About Section
            item {
                Text(
                    "About",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(16.dp, 8.dp)
                )
            }
            
            item {
                AboutCard()
            }
            
            // ── ADD NEW USER (Admin/Manager/Supervisor only) ──
            item {
                val userRole by viewModel.currentUserRole.collectAsState()
                val canAddUsers = userRole?.lowercase()?.trim() in
                    listOf("admin", "manager", "supervisor")

                if (canAddUsers) {
                    var showAddUserDialog by remember { mutableStateOf(false) }
                    var newUserName by remember { mutableStateOf("") }
                    var newUserEmail by remember { mutableStateOf("") }
                    var newUserRole by remember { mutableStateOf("Contractor") }

                    Spacer(modifier = Modifier.height(16.dp))
                    Card(modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("User Management",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                "Add new users. They receive a temporary password and must change it on first login.",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.Gray
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            Button(
                                onClick = { showAddUserDialog = true },
                                modifier = Modifier.fillMaxWidth(),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Color(0xFF1D9E75))
                            ) {
                                Text("Add New User")
                            }
                        }
                    }

                    if (showAddUserDialog) {
                        AlertDialog(
                            onDismissRequest = { showAddUserDialog = false },
                            title = { Text("Add New User") },
                            text = {
                                Column {
                                    OutlinedTextField(
                                        value = newUserName,
                                        onValueChange = { newUserName = it },
                                        label = { Text("Full Name") },
                                        modifier = Modifier.fillMaxWidth()
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    OutlinedTextField(
                                        value = newUserEmail,
                                        onValueChange = { newUserEmail = it },
                                        label = { Text("Email") },
                                        modifier = Modifier.fillMaxWidth()
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text("Role:", fontWeight = FontWeight.Bold)
                                    listOf("Contractor", "Supervisor", "Manager").forEach { role ->
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            modifier = Modifier.clickable { newUserRole = role }
                                        ) {
                                            RadioButton(
                                                selected = newUserRole == role,
                                                onClick = { newUserRole = role }
                                            )
                                            Text(role)
                                        }
                                    }
                                }
                            },
                            confirmButton = {
                                Button(onClick = {
                                    if (newUserName.isNotBlank() && newUserEmail.isNotBlank()) {
                                        viewModel.createNewUser(newUserName, newUserEmail, newUserRole)
                                        showAddUserDialog = false
                                        newUserName = ""
                                        newUserEmail = ""
                                        newUserRole = "Contractor"
                                    }
                                }) { Text("Create") }
                            },
                            dismissButton = {
                                TextButton(onClick = { showAddUserDialog = false }) { Text("Cancel") }
                            }
                        )
                    }
                }
            }

            // ── LOGOUT (visible to ALL users) ──
            item {
                Spacer(modifier = Modifier.height(24.dp))
                HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
                Spacer(modifier = Modifier.height(16.dp))
                Button(
                    onClick = {
                        com.google.firebase.auth.FirebaseAuth.getInstance().signOut()
                        onLogout()
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .height(52.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer,
                        contentColor = MaterialTheme.colorScheme.onErrorContainer),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Filled.ExitToApp, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Log Out", fontWeight = FontWeight.SemiBold)
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
fun ColorSchemeOptionWithImage(
    scheme: ColorScheme,
    isSelected: Boolean,
    onSelect: () -> Unit,
    onApply: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp, 8.dp)
            .clickable(onClick = onSelect),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) scheme.primary.copy(alpha = 0.1f) else Color.White
        ),
        border = if (isSelected) BorderStroke(3.dp, scheme.primary) else BorderStroke(1.dp, Color.LightGray),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 4.dp else 1.dp
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp)
        ) {
            // Preview Image (Large)
            Image(
                painter = painterResource(id = scheme.previewImageRes),
                contentDescription = scheme.displayName,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(150.dp)
                    .clip(RoundedCornerShape(8.dp))
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Title + Selection State
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    scheme.displayName,
                    style = MaterialTheme.typography.bodyLarge.copy(
                        fontWeight = FontWeight.Bold,
                        color = Color.Black
                    )
                )
                
                if (isSelected) {
                    Icon(
                        Icons.Filled.CheckCircle,
                        contentDescription = "Selected",
                        tint = scheme.primary,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Color Palette Preview (Mini swatches)
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
}

@Composable
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
fun AboutCard() {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp, 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "Space360",
                style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Bold)
            )
            Text(
                "v1.0.0 Beta",
                style = MaterialTheme.typography.bodySmall
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                "360° Field Inspection for Construction Sites",
                style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray)
            )
            
            // NEW: Developer Information
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                "Developed by",
                style = MaterialTheme.typography.labelSmall.copy(
                    fontWeight = FontWeight.Bold,
                    color = Color.Gray
                )
            )
            
            Text(
                "SGB Dev Apps",
                style = MaterialTheme.typography.bodySmall
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                "© 2026 Space360. All rights reserved.",
                style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray)
            )
        }
    }
}
