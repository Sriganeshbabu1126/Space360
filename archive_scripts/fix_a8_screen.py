import os
filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I wrote `Button(onClick = { }, modifier = Modifier.weight(1f).height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFFC107))) { Text("⏸️ Pause") }`
# Let's fix this button to actually pause.

old_pause = """                        Button(
                            onClick = { },
                            modifier = Modifier
                                .weight(1f)
                                .height(56.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFFFC107)
                            )
                        ) {
                            Text("⏸️ Pause")
                        }"""
new_pause = """                        Button(
                            onClick = { 
                                viewModel.pauseRecording() 
                                cameraViewModel.stopRecording()
                            },
                            modifier = Modifier
                                .weight(1f)
                                .height(56.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFFFC107)
                            )
                        ) {
                            Text("⏸️ Pause", color = Color.Black)
                        }"""
content = content.replace(old_pause, new_pause)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a8 screen")
