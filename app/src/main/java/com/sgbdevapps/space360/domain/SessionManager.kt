package com.sgbdevapps.space360.domain

import com.sgbdevapps.space360.domain.model.Site
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SessionManager @Inject constructor() {
    private val _selectedSite = MutableStateFlow<Site?>(null)
    val selectedSite: StateFlow<Site?> = _selectedSite.asStateFlow()

    fun setSelectedSite(site: Site?) {
        _selectedSite.value = site
    }
}
