import os
import re

dir_path = 'F:/Space360/app/src/main/java/com/sgbdevapps/space360'

# 1. ApiModels.kt
file1 = f'{dir_path}/data/remote/ApiModels.kt'
with open(file1, 'r', encoding='utf-8') as f:
    c1 = f.read()
# Replace val location: String with @SerializedName("address") val location: String? = null
c1 = re.sub(r'val location:\s*String,?', r'@SerializedName("address") val location: String? = null,', c1)
with open(file1, 'w', encoding='utf-8') as f:
    f.write(c1)

# 2. Site.kt
file2 = f'{dir_path}/domain/model/Site.kt'
with open(file2, 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = re.sub(r'val location:\s*String,?', r'val location: String? = null,', c2)
with open(file2, 'w', encoding='utf-8') as f:
    f.write(c2)

# 3. Entities.kt
file3 = f'{dir_path}/data/local/Entities.kt'
with open(file3, 'r', encoding='utf-8') as f:
    c3 = f.read()
# In SiteEntity, change val location: String to val location: String?
c3 = re.sub(r'val location:\s*String,?', r'val location: String?,', c3)
with open(file3, 'w', encoding='utf-8') as f:
    f.write(c3)

# 4. SiteRepositoryImpl.kt (actually no changes needed if it just passes site.location, but let's check)
# It uses: location = it.location
# Since both are String? now, it will just pass null along perfectly!
