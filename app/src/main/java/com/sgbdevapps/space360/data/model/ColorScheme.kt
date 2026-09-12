package com.sgbdevapps.space360.data.model

import androidx.annotation.ColorInt
import androidx.compose.ui.graphics.Color
import com.sgbdevapps.space360.R

enum class ColorScheme(
    val displayName: String,
    val previewImageRes: Int,
    val primary: Color,
    val secondary: Color,
    val accent: Color,
    val background: Color,
    val surface: Color
) {
    SUNSET(
        displayName = "Sunset Gradient",
        previewImageRes = R.drawable.colorscheme_1,
        primary = Color(0xFF1D9E75),
        secondary = Color(0xFFFF6B6B),
        accent = Color(0xFFFF9E64),
        background = Color.White,
        surface = Color(0xFFFAFAFA)
    ),
    OCEAN(
        displayName = "Ocean Blue",
        previewImageRes = R.drawable.colorscheme_2,
        primary = Color(0xFF0277BD),
        secondary = Color(0xFF01579B),
        accent = Color(0xFFFDD835),
        background = Color.White,
        surface = Color(0xFFF1F8E9)
    ),
    LAVENDER(
        displayName = "Lavender Dream",
        previewImageRes = R.drawable.colorscheme_3,
        primary = Color(0xFF6A1B9A),
        secondary = Color(0xFFC2185B),
        accent = Color(0xFFFFB74D),
        background = Color.White,
        surface = Color(0xFFF3E5F5)
    ),
    CORAL(
        displayName = "Coral Reef",
        previewImageRes = R.drawable.colorscheme_4,
        primary = Color(0xFFE65100),
        secondary = Color(0xFFFFA726),
        accent = Color(0xFF1565C0),
        background = Color.White,
        surface = Color(0xFFFFE0B2)
    ),
    SUNBURST(
        displayName = "Sunburst Yellow",
        previewImageRes = R.drawable.colorscheme_5,
        primary = Color(0xFFFDD835),
        secondary = Color(0xFFFFB300),
        accent = Color(0xFFFF6F00),
        background = Color.White,
        surface = Color(0xFFFFF9C4)
    )
}
