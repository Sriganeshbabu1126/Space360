package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import com.sgbdevapps.space360.domain.SessionManager
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val sessionManager: SessionManager
) : ViewModel() {
    val selectedSite = sessionManager.selectedSite
}
