import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if line.startswith('fun SyncBadge'):
        end_idx = i - 1
        break

func_content = '\n'.join(lines[:end_idx])
print(f"Open braces: {func_content.count('{')}")
print(f"Close braces: {func_content.count('}')}")
