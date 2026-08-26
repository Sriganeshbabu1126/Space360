package com.sgbdevapps.space360.presentation.viewmodels

import com.sgbdevapps.space360.domain.model.User
import com.sgbdevapps.space360.domain.repository.AuthRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class AuthViewModelTest {

    @Mock
    private lateinit var authRepository: AuthRepository

    private lateinit var viewModel: AuthViewModel
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setUp() {
        Dispatchers.setMain(testDispatcher)
        MockitoAnnotations.openMocks(this)
        
        // The ViewModel's init block calls checkLoginStatus, which launches a coroutine calling authRepository.isLoggedIn()
        // StandardTestDispatcher delays this execution until we yield, so it shouldn't crash on init immediately if we don't mock it yet,
        // but we can mock it here for safety.
        
        viewModel = AuthViewModel(authRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun testLoginSuccess() = runTest {
        val testUser = User("1", "test@example.com", "Test User", "Contractor")
        whenever(authRepository.login("test@example.com", "password123"))
            .thenReturn(Result.success(testUser))

        viewModel.login("test@example.com", "password123")
    }

    @Test
    fun testLoginFailure() = runTest {
        whenever(authRepository.login("test@example.com", "wrong")).thenReturn(
            Result.failure(Exception("Invalid credentials"))
        )

        viewModel.login("test@example.com", "wrong")
    }
}
