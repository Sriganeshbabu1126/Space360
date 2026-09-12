import os

filepath = "app/build.gradle.kts"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "dependencies {" in line and "androidx.core:core-ktx" in "".join(lines):
        # ensure we only append after the main dependencies block
        # wait, just appending at the end of the block is safer.
        pass

# Append at the end of the file inside dependencies block
# Since the file might have multiple, let's just append at the very end
with open(filepath, "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line)
    f.write("\n")
    f.write("dependencies {\n")
    f.write("    implementation(\"androidx.datastore:datastore-preferences:1.0.0\")\n")
    f.write("    implementation(\"io.coil-kt:coil-compose:2.4.0\")\n")
    f.write("}\n")
