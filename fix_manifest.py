import os

filepath = "app/src/main/AndroidManifest.xml"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('android:icon="@mipmap/ic_launcher"', 'android:icon="@drawable/app_logo"')
content = content.replace('android:roundIcon="@mipmap/ic_launcher_round"', 'android:roundIcon="@drawable/app_logo"')
content = content.replace('android:label="@string/app_name"', 'android:label="@string/app_name"\n        android:logo="@drawable/app_logo"')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
