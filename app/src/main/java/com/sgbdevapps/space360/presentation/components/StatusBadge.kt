package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun StatusBadge(status: String) {
    val color = when (status) {
        "Open" -> Color(0xFF4CAF50)
        "In Progress", "In Review" -> Color(0xFF2196F3)
        "Done", "Pending" -> Color(0xFFFFA726)
        "Closed" -> Color(0xFF9E9E9E)
        "Critical" -> Color(0xFFD32F2F)
        else -> Color(0xFF9E9E9E)
    }

    Text(
        text = status,
        color = Color.White,
        modifier = Modifier
            .background(color, shape = androidx.compose.foundation.shape.RoundedCornerShape(4.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp)
    )
}
