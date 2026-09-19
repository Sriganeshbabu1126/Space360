import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Fix application ID
content = content.replace('applicationId = "com.space360.mobile"', 'applicationId = "com.sgbdevapps.space360"')
content = content.replace('applicationId = "com.example.space360"', 'applicationId = "com.sgbdevapps.space360"')

# Ensure packaging block is there
if "META-INF/DEPENDENCIES" not in content:
    packaging_block = """    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
            excludes += "META-INF/DEPENDENCIES"
            excludes += "META-INF/LICENSE"
            excludes += "META-INF/LICENSE.txt"
            excludes += "META-INF/license.txt"
            excludes += "META-INF/NOTICE"
            excludes += "META-INF/NOTICE.txt"
            excludes += "META-INF/notice.txt"
        }
    }"""
    if "packaging {" in content:
        # replace the existing simple packaging block
        content = content.replace('    packaging {\n        resources {\n            excludes += "/META-INF/{AL2.0,LGPL2.1}"\n        }\n    }', packaging_block)
    else:
        # just inject it before buildTypes
        content = content.replace('    buildTypes {', packaging_block + '\n\n    buildTypes {')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
