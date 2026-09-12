import os
import re

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add needed imports
if "import coil.compose.AsyncImage" not in content:
    content = content.replace("import androidx.compose.ui.platform.LocalContext", "import androidx.compose.ui.platform.LocalContext\nimport coil.compose.AsyncImage\nimport coil.request.ImageRequest\nimport androidx.compose.ui.text.style.TextAlign\nimport androidx.compose.material.icons.outlined.Map\nimport com.sgbdevapps.space360.R\nimport androidx.compose.foundation.Image\nimport androidx.compose.ui.res.painterResource")

floor_plan_composable = """@Composable
fun FloorPlanSection(viewModel: com.sgbdevapps.space360.presentation.viewmodels.PathCaptureViewModel) {
    val state by viewModel.floorPlanLoadState.collectAsState()

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(280.dp)
            .padding(horizontal = 16.dp, vertical = 8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            when (state) {
                // Loading spinner
                is FloorPlanLoadState.Loading -> {
                    Box(
                        modifier = Modifier.fillMaxSize()
                            .background(MaterialTheme.colorScheme.surfaceVariant),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text("Loading floor plan...",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                }
                // LAYER 1: Real floor plan from backend
                is FloorPlanLoadState.Loaded -> {
                    val url = (state as FloorPlanLoadState.Loaded).url
                    AsyncImage(
                        model = ImageRequest.Builder(LocalContext.current)
                            .data(url)
                            .crossfade(true)
                            .placeholder(R.drawable.floor_plan_placeholder)
                            .error(R.drawable.floor_plan_placeholder)
                            .build(),
                        contentDescription = "Floor plan",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                    Box(modifier = Modifier.fillMaxSize().padding(8.dp),
                        contentAlignment = Alignment.TopStart) {
                        Surface(color = MaterialTheme.colorScheme.primary.copy(alpha = 0.75f),
                            shape = RoundedCornerShape(4.dp)) {
                            Text("Floor Plan",
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White)
                        }
                    }
                }
                // LAYER 2: No floor plan uploaded
                is FloorPlanLoadState.NoFloorPlan -> {
                    Box(modifier = Modifier.fillMaxSize()) {
                        Image(
                            painter = painterResource(id = R.drawable.floor_plan_placeholder),
                            contentDescription = "Floor plan placeholder",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Fit
                        )
                        Box(modifier = Modifier.fillMaxSize().padding(8.dp),
                            contentAlignment = Alignment.BottomCenter) {
                            Surface(color = Color.Black.copy(alpha = 0.45f),
                                shape = RoundedCornerShape(4.dp)) {
                                Text("No floor plan uploaded for this project",
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Color.White)
                            }
                        }
                    }
                }
                // LAYER 3: No project selected or error
                is FloorPlanLoadState.NoProject,
                is FloorPlanLoadState.Error -> {
                    Box(
                        modifier = Modifier.fillMaxSize()
                            .background(MaterialTheme.colorScheme.surfaceVariant),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally,
                            modifier = Modifier.padding(16.dp)) {
                            Icon(imageVector = Icons.Outlined.Map,
                                contentDescription = null,
                                modifier = Modifier.size(48.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                if (state is FloorPlanLoadState.NoProject)
                                    "Select a project to view floor plan"
                                else
                                    "Floor plan unavailable",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }
            }
        }
    }
}
"""

content = content + "\n\n" + floor_plan_composable

# Now we need to replace the old Card showing AsyncImage in CaptureScreen with FloorPlanSection(viewModel)
old_card_pattern = r"// Map Placeholder.*?Card\([\s\S]*?AsyncImage\([\s\S]*?\}\s*\)\s*\}\s*\}"
match = re.search(old_card_pattern, content)
if match:
    content = content.replace(match.group(0), "FloorPlanSection(viewModel)")
else:
    print("Could not find the old map placeholder card via regex!")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
