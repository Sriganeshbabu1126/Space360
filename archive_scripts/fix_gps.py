import os

filepath = "app/src/main/java/com/sgbdevapps/space360/service/GpsTrackingService.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_comp = """    companion object {
        private var _recordingSession: com.sgbdevapps.space360.service.RecordingSession? = null
        fun setRecordingSession(session: com.sgbdevapps.space360.service.RecordingSession?) {
            _recordingSession = session
        }"""
content = content.replace("    companion object {", new_comp)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
