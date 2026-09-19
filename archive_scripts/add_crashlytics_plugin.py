import os

filepath = "build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'id("com.google.gms.google-services") version "4.4.1" apply false',
    'id("com.google.gms.google-services") version "4.4.1" apply false\n    id("com.google.firebase.crashlytics") version "2.9.9" apply false'
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
