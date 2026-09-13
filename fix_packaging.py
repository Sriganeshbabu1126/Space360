import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_packaging = """    packaging {
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

content = content.replace('    packaging {\n        resources {\n            excludes += "/META-INF/{AL2.0,LGPL2.1}"\n        }\n    }', new_packaging)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
