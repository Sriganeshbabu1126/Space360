import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add missing plugins
if 'id("com.google.firebase.crashlytics")' not in content:
    content = content.replace(
        'id("com.google.gms.google-services")',
        'id("com.google.gms.google-services")\n    id("com.google.firebase.crashlytics")'
    )

# Append dependencies
missing_deps = """
    // Recovered missing dependencies
    implementation("com.jakewharton.timber:timber:5.0.1")
    implementation("com.google.firebase:firebase-crashlytics")
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.accompanist:accompanist-permissions:0.35.1-alpha")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.work:work-runtime-ktx:2.9.0")
    implementation("androidx.hilt:hilt-work:1.2.0")
    ksp("androidx.hilt:hilt-compiler:1.2.0")
    
    // Google Sheets API
    implementation("com.google.api-client:google-api-client-android:2.2.0")
    implementation("com.google.apis:google-api-services-sheets:v4-rev20230815-2.0.0")
    implementation("com.google.auth:google-auth-library-oauth2-http:1.19.0")
"""

content = content.replace(
    'implementation("com.google.android.gms:play-services-location:21.3.0")',
    'implementation("com.google.android.gms:play-services-location:21.3.0")' + missing_deps
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
