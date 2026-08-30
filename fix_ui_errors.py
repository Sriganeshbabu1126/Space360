import os
import re

dir_path = 'F:/Space360/app/src/main/java/com/sgbdevapps/space360'

# 1. AuthRepositoryImpl.kt
file1 = f'{dir_path}/data/repository/AuthRepositoryImpl.kt'
with open(file1, 'r', encoding='utf-8') as f:
    c1 = f.read()
# Find where it returns User with Int id
c1 = re.sub(r'id = .*\.hashCode\(\),?', r'id = firebaseUser.uid,', c1)
c1 = re.sub(r'id = 0,?', r'id = "",', c1) 
with open(file1, 'w', encoding='utf-8') as f:
    f.write(c1)

# 2. CommentThread.kt
file2 = f'{dir_path}/presentation/components/CommentThread.kt'
with open(file2, 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = re.sub(r'currentUserId:\s*Int', r'currentUserId: String', c2)
with open(file2, 'w', encoding='utf-8') as f:
    f.write(c2)

# 3. PhotoGallery.kt
file3 = f'{dir_path}/presentation/components/PhotoGallery.kt'
if os.path.exists(file3):
    with open(file3, 'r', encoding='utf-8') as f:
        c3 = f.read()
    c3 = re.sub(r'id = \d+', r'id = "0"', c3)
    c3 = re.sub(r'issueId = \d+', r'issueId = "0"', c3)
    with open(file3, 'w', encoding='utf-8') as f:
        f.write(c3)

# 4. NavGraph.kt
file4 = f'{dir_path}/presentation/navigation/NavGraph.kt'
with open(file4, 'r', encoding='utf-8') as f:
    c4 = f.read()
c4 = re.sub(r'NavType\.IntType', r'NavType.StringType', c4)
c4 = re.sub(r'getInt\(', r'getString(', c4)
# In NavGraph, the routes are sites/{siteId} where siteId is now string, so getString is used.
# But what about the nav argument default value if any?
with open(file4, 'w', encoding='utf-8') as f:
    f.write(c4)
