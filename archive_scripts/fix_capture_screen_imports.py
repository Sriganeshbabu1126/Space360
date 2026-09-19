import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/CaptureScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

imports_to_add = """
import coil.request.ImageRequest
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.material.icons.outlined.Map
import com.sgbdevapps.space360.R
import androidx.compose.foundation.Image
import androidx.compose.ui.res.painterResource
"""

content = content.replace("import coil.compose.AsyncImage", "import coil.compose.AsyncImage" + imports_to_add)

# Replace currentFloorPlanUrl usage in FloorPlanLocationPicker
old_picker = """            if (showLocationPicker) {
                FloorPlanLocationPicker(
                    floorPlanUrl = currentFloorPlanUrl,
                    onLocationSelected = { lat, lng -> viewModel.pinLocationInteractive(lat, lng) },
                    onDismiss = { viewModel.closeLocationPicker() }
                )
            }"""
new_picker = """            if (showLocationPicker) {
                val floorPlanUrl = (viewModel.floorPlanLoadState.collectAsState().value as? FloorPlanLoadState.Loaded)?.url
                FloorPlanLocationPicker(
                    floorPlanUrl = floorPlanUrl,
                    onLocationSelected = { lat, lng -> viewModel.pinLocationInteractive(lat, lng) },
                    onDismiss = { viewModel.closeLocationPicker() }
                )
            }"""
if old_picker in content:
    content = content.replace(old_picker, new_picker)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
