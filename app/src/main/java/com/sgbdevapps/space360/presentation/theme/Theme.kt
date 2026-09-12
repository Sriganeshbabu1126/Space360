package com.sgbdevapps.space360.presentation.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat
import com.sgbdevapps.space360.data.model.ColorScheme

@Composable
fun Space360Theme(
    colorScheme: ColorScheme = ColorScheme.SUNSET,
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colors = lightColorScheme(
        primary = colorScheme.primary,
        onPrimary = Color.White,
        secondary = colorScheme.secondary,
        onSecondary = Color.White,
        tertiary = colorScheme.accent,
        onTertiary = Color.White,
        background = colorScheme.background,
        onBackground = Color.Black,
        surface = colorScheme.surface,
        onSurface = Color.Black,
        error = Color(0xFFD32F2F),
        onError = Color.White
    )
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colors.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colors,
        content = content
    )
}
