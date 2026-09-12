import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add showPhotoOptions state variable
old_vars = """    var photoUri by remember { mutableStateOf<Uri?>(null) }"""
new_vars = """    var photoUri by remember { mutableStateOf<Uri?>(null) }
    var showPhotoOptions by remember { mutableStateOf(false) }"""
content = content.replace(old_vars, new_vars)

# 2. Add gallery picker launcher
old_camera_launcher = """    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->"""

new_gallery_picker = """    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            viewModel.uploadPhotoUri(it)
        }
    }
    
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->"""

content = content.replace(old_camera_launcher, new_gallery_picker)

# 3. Modify "Add Evidence Photo" button and add AlertDialog
old_add_photo = """                    // Add Photo Action
                    Button(
                        onClick = { cameraPermissionLauncher.launch(android.Manifest.permission.CAMERA) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Filled.PhotoCamera, contentDescription = "Add Photo")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Add Evidence Photo")
                    }"""

new_add_photo = """                    // Add Photo Action
                    Button(
                        onClick = { showPhotoOptions = true },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Filled.PhotoCamera, contentDescription = "Add Photo")
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Add Evidence Photo")
                    }
                    
                    if (showPhotoOptions) {
                        AlertDialog(
                            onDismissRequest = { showPhotoOptions = false },
                            title = { Text("Add Photo") },
                            text = { Text("Choose photo source") },
                            confirmButton = {
                                Button(
                                    onClick = {
                                        cameraPermissionLauncher.launch(android.Manifest.permission.CAMERA)
                                        showPhotoOptions = false
                                    }
                                ) {
                                    Text("📷 Camera")
                                }
                            },
                            dismissButton = {
                                Button(
                                    onClick = {
                                        galleryLauncher.launch("image/*")
                                        showPhotoOptions = false
                                    }
                                ) {
                                    Text("🖼️ Gallery")
                                }
                            }
                        )
                    }"""
content = content.replace(old_add_photo, new_add_photo)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a1 screen")
