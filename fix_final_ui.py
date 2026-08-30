import os
import re

dir_path = 'F:/Space360/app/src/main/java/com/sgbdevapps/space360'

# 1. CommentThread.kt
file2 = f'{dir_path}/presentation/components/CommentThread.kt'
with open(file2, 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = re.sub(r'if\s*\(comment\.id\s*<\s*0\)', r'if (false)', c2)
with open(file2, 'w', encoding='utf-8') as f:
    f.write(c2)

# 2. PhotoGallery.kt
file3 = f'{dir_path}/presentation/components/PhotoGallery.kt'
with open(file3, 'r', encoding='utf-8') as f:
    c3 = f.read()
c3 = re.sub(r'if\s*\(photo\.id\s*<\s*0\)', r'if (false)', c3)
with open(file3, 'w', encoding='utf-8') as f:
    f.write(c3)

# 3. NavGraph.kt
file4 = f'{dir_path}/presentation/navigation/NavGraph.kt'
with open(file4, 'r', encoding='utf-8') as f:
    c4 = f.read()
# Replace ?.getString("siteId")?.toInt() ?: 0 with ?.getString("siteId") ?: ""
c4 = re.sub(r'\?\.getString\("siteId"\)\?\.toInt\(\) \?: 0', r'?.getString("siteId") ?: ""', c4)
c4 = re.sub(r'\?\.getString\("issueId"\)\?\.toInt\(\) \?: 0', r'?.getString("issueId") ?: ""', c4)
with open(file4, 'w', encoding='utf-8') as f:
    f.write(c4)

