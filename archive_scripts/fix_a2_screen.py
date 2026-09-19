import os

filepath = "app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add CommentsSection
# We need to find where to put it. Currently it probably ends with the Add Photo block or something.
# Let's insert it after the IssueDetails section.

new_comments_composable = """

@Composable
fun CommentsSection(
    issueId: String,
    comments: List<IssueComment>,
    onAddComment: (String) -> Unit
) {
    var newCommentText by remember { mutableStateOf("") }
    
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Text(
            "Comments",
            style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Bold)
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        // Comment input field
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp)
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                TextField(
                    value = newCommentText,
                    onValueChange = { newCommentText = it },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Add a comment...") },
                    minLines = 3,
                    maxLines = 5
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Button(
                    onClick = {
                        if (newCommentText.isNotBlank()) {
                            onAddComment(newCommentText)
                            newCommentText = ""
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    )
                ) {
                    Text("Post Comment", color = Color.White)
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Comments list
        if (comments.isEmpty()) {
            Text(
                "No comments yet",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        } else {
            comments.forEach { comment ->
                CommentCard(comment)
            }
        }
    }
}

@Composable
fun CommentCard(comment: IssueComment) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    comment.authorName,
                    style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold)
                )
                Text(
                    comment.createdAt,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                comment.text,
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
"""

if "fun CommentsSection" not in content:
    content += new_comments_composable
    
# Now find where to call CommentsSection
# It should be inside the LazyColumn in IssueDetailScreen.kt

# Currently there might be a call to CommentsSection or it might be missing entirely.
# Let's just find the end of the item { ... } that holds the details and add CommentsSection.
# In my previous changes to IssueDetailScreen.kt, it's a LazyColumn with maybe one big item, or multiple items.
# Let's append an item { CommentsSection(...) } to the LazyColumn.

if "CommentsSection(issueId = issueId, comments = issue?.comments ?: emptyList(), onAddComment = { viewModel.addComment(it) })" not in content:
    # Just replace `            } // End of LazyColumn` with the item
    content = content.replace(
        "            }\n        }\n    }\n}\n",
        "            }\n            item {\n                CommentsSection(issueId = issueId, comments = issue?.comments ?: emptyList(), onAddComment = { viewModel.addComment(it) })\n            }\n        }\n    }\n}\n"
    )

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Done a2 screen")
