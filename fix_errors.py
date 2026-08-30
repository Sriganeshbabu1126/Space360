import os
import re

dir_path = 'F:/Space360/app/src/main/java/com/sgbdevapps/space360'

for root, dirs, files in os.walk(dir_path):
    for file in files:
        if file.endswith('.kt'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # IssueDetailViewModel.kt
            if 'IssueDetailViewModel.kt' in file:
                new_content = re.sub(
                    r'val userId = authRepository\.getCurrentUser\(\)\.getOrNull\(\)\?\.id\?\.toIntOrNull\(\) \?: 0',
                    'val userId = authRepository.getCurrentUser().getOrNull()?.id ?: ""',
                    new_content
                )
                new_content = re.sub(
                    r'id = -\(System\.currentTimeMillis\(\) / 1000\)\.toInt\(\)',
                    'id = java.util.UUID.randomUUID().toString()',
                    new_content
                )
            
            # IssueRepository.kt / IssueRepositoryImpl.kt
            if 'IssueRepository' in file:
                new_content = re.sub(r'contractorId:\s*Int', 'contractorId: String', new_content)
                new_content = re.sub(
                    r'id = -\(System\.currentTimeMillis\(\) / 1000\)\.toInt\(\)',
                    'id = java.util.UUID.randomUUID().toString()',
                    new_content
                )
            
            # IssuesListViewModel.kt
            if 'IssuesListViewModel.kt' in file:
                new_content = re.sub(r'siteId:\s*Int', 'siteId: String', new_content)
                new_content = re.sub(r'id:\s*Int', 'id: String', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Fixed errors in {file}')
