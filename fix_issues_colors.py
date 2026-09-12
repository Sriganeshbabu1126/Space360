import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace background colors
old_bg_colors = """                        "open" -> Color(0xFFD32F2F).copy(alpha = 0.1f)
                        "in review" -> Color(0xFFFFC107).copy(alpha = 0.1f)
                        "closed" -> Color(0xFF4CAF50).copy(alpha = 0.1f)"""
                        
new_bg_colors = """                        "open" -> Color(0xFF2196F3).copy(alpha = 0.1f)
                        "in review" -> Color(0xFFFF9800).copy(alpha = 0.1f)
                        "closed" -> Color(0xFF4CAF50).copy(alpha = 0.1f)"""
                        
content = content.replace(old_bg_colors, new_bg_colors)

# Replace text colors
old_text_colors = """                                "open" -> Color(0xFFD32F2F)
                                "in review" -> Color(0xFFFF9800)
                                "closed" -> Color(0xFF4CAF50)"""

new_text_colors = """                                "open" -> Color(0xFF2196F3)
                                "in review" -> Color(0xFFFF9800)
                                "closed" -> Color(0xFF4CAF50)"""

content = content.replace(old_text_colors, new_text_colors)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
