
import re

with open('app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt', 'r') as f:
    content = f.read()
    
content = content.replace('android.util.Log.d("PathRepo", "Saving path', 'android.util.Log.e("SPACE360_DEBUG", "Saving path')
content = content.replace('android.util.Log.d("PathRepo", "Enqueueing immediate', 'android.util.Log.e("SPACE360_DEBUG", "Enqueueing immediate')

with open('app/src/main/java/com/sgbdevapps/space360/data/repository/PathRepositoryImpl.kt', 'w') as f:
    f.write(content)

with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'r') as f:
    content = f.read()

content = content.replace('android.util.Log.d("SyncWorker"', 'android.util.Log.e("SPACE360_DEBUG"')
content = content.replace('android.util.Log.e("SyncWorker"', 'android.util.Log.e("SPACE360_DEBUG"')

with open('app/src/main/java/com/sgbdevapps/space360/data/sync/SyncWorker.kt', 'w') as f:
    f.write(content)

