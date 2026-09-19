import os

filepath = "app/src/main/java/com/sgbdevapps/space360/di/DatabaseModule.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

imports = """
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.PreferenceDataStoreFactory
import androidx.datastore.preferences.preferencesDataStoreFile
import java.io.File
"""
if "import androidx.datastore" not in content:
    content = content.replace("import android.content.Context\n", "import android.content.Context\n" + imports)

provider = """
    @Provides
    @Singleton
    fun provideDataStore(@ApplicationContext context: Context): DataStore<Preferences> {
        return PreferenceDataStoreFactory.create(
            produceFile = { context.preferencesDataStoreFile("space360_prefs") }
        )
    }
"""

if "fun provideDataStore" not in content:
    content = content.replace("object DatabaseModule {\n", "object DatabaseModule {\n" + provider)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
