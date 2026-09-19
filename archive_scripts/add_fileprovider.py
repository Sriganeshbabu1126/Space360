import os

filepath = "app/src/main/AndroidManifest.xml"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

provider_xml = """
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
"""

if "androidx.core.content.FileProvider" not in content:
    content = content.replace("</application>", provider_xml + "\n    </application>")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

os.makedirs("app/src/main/res/xml", exist_ok=True)
paths_xml = """<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <cache-path name="images" path="/" />
    <external-files-path name="images" path="Pictures" />
</paths>
"""
with open("app/src/main/res/xml/file_paths.xml", "w", encoding="utf-8") as f:
    f.write(paths_xml)

print("Done")
