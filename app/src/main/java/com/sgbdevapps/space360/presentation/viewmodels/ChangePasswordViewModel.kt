package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.firebase.auth.FirebaseAuth
import com.sgbdevapps.space360.data.repository.UserManagementRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import timber.log.Timber
import javax.inject.Inject

@HiltViewModel
class ChangePasswordViewModel @Inject constructor(
    private val userManagementRepository: UserManagementRepository
) : ViewModel() {

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    fun changePassword(newPassword: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val user = FirebaseAuth.getInstance().currentUser
                    ?: throw Exception("Not logged in")

                user.updatePassword(newPassword).await()

                userManagementRepository.markPasswordChanged(
                    email = user.email ?: "",
                    newPassword = newPassword
                )

                Timber.i("Password changed successfully for ${user.email}")
                onSuccess()

            } catch (e: Exception) {
                Timber.e(e, "Password change failed")
                _error.value = e.message ?: "Failed to change password"
            } finally {
                _isLoading.value = false
            }
        }
    }
}
