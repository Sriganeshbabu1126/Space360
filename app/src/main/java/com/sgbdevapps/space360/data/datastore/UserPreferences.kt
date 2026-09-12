package com.sgbdevapps.space360.data.datastore

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import com.sgbdevapps.space360.data.model.ColorScheme
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class UserPreferences @Inject constructor(
    private val dataStore: DataStore<Preferences>
) {
    companion object {
        val SELECTED_COLOR_SCHEME = stringPreferencesKey("selected_color_scheme")
    }
    
    val selectedColorScheme: Flow<String> = dataStore.data
        .map { preferences ->
            preferences[SELECTED_COLOR_SCHEME] ?: ColorScheme.SUNSET.name
        }
    
    suspend fun setColorScheme(scheme: ColorScheme) {
        dataStore.edit { preferences ->
            preferences[SELECTED_COLOR_SCHEME] = scheme.name
        }
    }
}
