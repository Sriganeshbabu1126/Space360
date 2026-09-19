import os

filepath = "app/src/main/AndroidManifest.xml"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

queries_block = """
    <queries>
        <intent>
            <action android:name="android.media.action.IMAGE_CAPTURE" />
        </intent>
    </queries>

    <application"""
content = content.replace("<application", queries_block)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
