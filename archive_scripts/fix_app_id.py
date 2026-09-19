import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('applicationId = "com.space360.mobile"', 'applicationId = "com.sgbdevapps.space360"')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
