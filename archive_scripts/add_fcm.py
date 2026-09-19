import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'implementation("com.google.firebase:firebase-auth-ktx")',
    'implementation("com.google.firebase:firebase-auth-ktx")\n    implementation("com.google.firebase:firebase-messaging-ktx")'
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
