import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

deps = """
    // Google Sheets API
    implementation("com.google.api-client:google-api-client-android:2.2.0")
    implementation("com.google.apis:google-api-services-sheets:v4-rev20230815-2.0.0")
    implementation("com.google.auth:google-auth-library-oauth2-http:1.19.0")
}
"""

content = content.replace("\n}", deps)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
