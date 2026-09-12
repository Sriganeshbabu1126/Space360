import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_box = """            // Map Placeholder
            // Floor plan or map
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .background(Color.LightGray, RoundedCornerShape(8.dp)),
                contentAlignment = Alignment.Center
            ) {
                if (currentFloorPlanUrl != null) {
                    AsyncImage(
                        model = currentFloorPlanUrl,
                        contentDescription = "Floor plan",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                } else {
                    Text("No floor plan available", color = Color.Gray)
                }
                
                if (isLocationPinned) {
                    Icon(
                        Icons.Filled.LocationOn,
                        contentDescription = "Location pinned",
                        tint = Color.Red,
                        modifier = Modifier.size(48.dp)
                    )
                }
            }"""
new_box = """            // Map Placeholder
            Box(modifier = Modifier.fillMaxWidth().height(300.dp)) {
                FloorPlanSection(viewModel)
                if (isLocationPinned) {
                    Icon(
                        Icons.Filled.LocationOn,
                        contentDescription = "Location pinned",
                        tint = Color.Red,
                        modifier = Modifier.size(48.dp).align(Alignment.Center)
                    )
                }
            }"""

if old_box in content:
    content = content.replace(old_box, new_box)
else:
    print("Could not find the old box block!")

# Remove currentFloorPlanUrl collecting
old_collect = "val currentFloorPlanUrl by viewModel.currentFloorPlanUrl.collectAsState()"
if old_collect in content:
    content = content.replace(old_collect, "")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
