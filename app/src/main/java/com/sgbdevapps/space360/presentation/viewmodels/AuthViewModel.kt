package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.domain.model.User
import com.sgbdevapps.space360.domain.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState: StateFlow<AuthState> = _authState

    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn

    init {
        checkLoginStatus()
    }

    private val _mustChangePassword = MutableStateFlow(false)
    val mustChangePassword: StateFlow<Boolean> = _mustChangePassword

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.login(email, password)
            if (result.isSuccess) {
                val user = result.getOrNull()!!
                com.sgbdevapps.space360.utils.CrashlyticsHelper.setUserContext(userId = user.id, email = user.email)
                
                if (password == "welcomespace360") {
                    _mustChangePassword.value = true
                } else {
                    _isLoggedIn.value = true
                    _authState.value = AuthState.Success(user)
                }
            } else {
                _authState.value = AuthState.Error(result.exceptionOrNull()?.message ?: "Login failed")
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            com.sgbdevapps.space360.utils.CrashlyticsHelper.clearUserContext(); authRepository.logout()
            _isLoggedIn.value = false
            _authState.value = AuthState.Idle
        }
    }

    private fun checkLoginStatus() {
        viewModelScope.launch {
            val loggedIn = authRepository.isLoggedIn()
            _isLoggedIn.value = loggedIn
            if (loggedIn) {
                authRepository.getCurrentUser().getOrNull()?.let {
                    com.sgbdevapps.space360.utils.CrashlyticsHelper.setUserContext(userId = it.id, email = it.email); _authState.value = AuthState.Success(it)
                }
            }
        }
    }

    sealed class AuthState {
        object Idle : AuthState()
        object Loading : AuthState()
        data class Success(val user: User) : AuthState()
        data class Error(val message: String) : AuthState()
    }
}
