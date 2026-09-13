import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_str = """@HiltViewModel
import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext

@dagger.hilt.android.lifecycle.HiltViewModel"""
new_str = """import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext

@HiltViewModel"""
content = content.replace(old_str, new_str)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
