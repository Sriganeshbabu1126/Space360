import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_gal = """      val galleryLauncher = rememberLauncherForActivityResult(
          contract = ActivityResultContracts.GetContent()
      ) { uri ->
          uri?.let {
              viewModel.uploadPhotoUri(it)
          }
      }"""
new_gal = """      val galleryLauncher = rememberLauncherForActivityResult(
          contract = ActivityResultContracts.GetContent()
      ) { uri ->
          timber.log.Timber.d("PHOTO_DEBUG: gallery result uri=$uri")
          uri?.let {
              viewModel.addPhotoToIssue(issueId, it)
          }
      }"""
content = content.replace(old_gal, new_gal)

old_cam = """      val cameraLauncher = rememberLauncherForActivityResult(
          contract = ActivityResultContracts.TakePicture()
      ) { success ->
          if (success && photoUri != null) {
              val result = com.sgbdevapps.space360.utils.PhotoCompressionHelper.compressPhotoIfNeeded(context, photoUri!!)
              if (result.success) {
                  android.widget.Toast.makeText(context, "Compressed successfully", android.widget.Toast.LENGTH_SHORT).show()
                  viewModel.uploadPhotoUri(Uri.parse("file://${result.compressedFilePath}"))
              } else {
                  android.widget.Toast.makeText(context, "Failed to compress", android.widget.Toast.LENGTH_LONG).show()
              }
          }
      }"""
new_cam = """      val cameraLauncher = rememberLauncherForActivityResult(
          contract = ActivityResultContracts.TakePicture()
      ) { success ->
          timber.log.Timber.d("PHOTO_DEBUG: camera result success=$success, uri=$photoUri")
          if (success && photoUri != null) {
              val result = com.sgbdevapps.space360.utils.PhotoCompressionHelper.compressPhotoIfNeeded(context, photoUri!!)
              if (result.success) {
                  viewModel.addPhotoToIssue(issueId, Uri.parse("file://${result.compressedFilePath}"))
              } else {
                  viewModel.addPhotoToIssue(issueId, photoUri!!)
              }
          }
      }"""
content = content.replace(old_cam, new_cam)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
