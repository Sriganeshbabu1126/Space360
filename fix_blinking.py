import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure imports for animation are present
imports_to_add = [
    "import androidx.compose.animation.core.*",
    "import androidx.compose.ui.draw.alpha"
]
for imp in imports_to_add:
    if imp not in content:
        content = content.replace("import androidx.compose.ui.Modifier", f"{imp}\nimport androidx.compose.ui.Modifier")

old_timer = """            // Recording Timer (Large, Bold)
            if (isRecording) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Filled.Circle,
                        contentDescription = "Recording",
                        tint = Color.Red,
                        modifier = Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = formatDuration(recordingDurationSeconds),
                        style = MaterialTheme.typography.headlineSmall.copy(
                            fontSize = 36.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.Black
                        )
                    )
                }
                Spacer(modifier = Modifier.height(20.dp))
            }"""

new_timer = """            // Insta Recording Status
            if (isRecording) {
                val infiniteTransition = rememberInfiniteTransition(label = "recording_blink")
                val alpha by infiniteTransition.animateFloat(
                    initialValue = 1f,
                    targetValue = 0.2f,
                    animationSpec = infiniteRepeatable(
                        animation = tween(800, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    ),
                    label = "alpha_blink"
                )

                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        "Insta Recording Status",
                        style = MaterialTheme.typography.titleMedium.copy(
                            color = Color.Gray,
                            fontWeight = FontWeight.SemiBold
                        )
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Filled.Circle,
                            contentDescription = "Recording",
                            tint = Color.Red,
                            modifier = Modifier
                                .size(16.dp)
                                .clip(CircleShape)
                                .alpha(alpha)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = formatDuration(recordingDurationSeconds),
                            style = MaterialTheme.typography.headlineSmall.copy(
                                fontSize = 36.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.Black
                            )
                        )
                    }
                }
                Spacer(modifier = Modifier.height(20.dp))
            }"""

if "Insta Recording Status" not in content:
    content = content.replace(old_timer, new_timer)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
