import os

filepath = "settings.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_repo = """        mavenCentral()
    }
}"""
new_repo = """        mavenCentral()
        maven { url = uri("https://packages.confluent.io/maven/") }
    }
}"""
content = content.replace(old_repo, new_repo)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
