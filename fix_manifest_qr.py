import os

filepath = "app/src/main/AndroidManifest.xml"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add meta-data
meta = """
        <!-- Add ML Kit model metadata -->
        <meta-data
            android:name="com.google.mlkit.vision.DEPENDENCIES"
            android:value="barcode_detection" />
"""
if "barcode_detection" not in content:
    content = content.replace("</application>", meta + "\n    </application>")

# Add Deep Link
deep_link = """
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data
                    android:scheme="space360"
                    android:host="issue"
                    android:pathPrefix="/" />
            </intent-filter>
"""
if "android:scheme=\"space360\"" not in content:
    content = content.replace('                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>', '                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>' + deep_link)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
