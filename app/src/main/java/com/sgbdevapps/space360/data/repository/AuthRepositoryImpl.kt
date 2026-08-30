package com.sgbdevapps.space360.data.repository

import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import com.sgbdevapps.space360.data.local.UserDao
import com.sgbdevapps.space360.data.local.UserEntity

import com.sgbdevapps.space360.data.remote.AuthService
import com.sgbdevapps.space360.data.remote.LoginRequest
import com.sgbdevapps.space360.domain.model.User
import com.sgbdevapps.space360.domain.repository.AuthRepository
import kotlinx.coroutines.tasks.await
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val firebaseAuth: FirebaseAuth,
    private val authService: AuthService,
    private val userDao: UserDao
) : AuthRepository {

    override suspend fun login(email: String, password: String): Result<User> {
        return try {
            // Firebase Auth
            val authResult = firebaseAuth.signInWithEmailAndPassword(email, password).await()
            val firebaseUser = authResult.user ?: throw Exception("User is null after login")

            // Create domain model
            val user = User(
                id = firebaseUser.uid,
                email = firebaseUser.email ?: "",
                displayName = firebaseUser.displayName,
                role = "Contractor"
            )

            // Cache locally
            userDao.insertUser(
                UserEntity(
                    id = firebaseUser.uid,
                    email = user.email,
                    displayName = user.displayName,
                    role = user.role
                )
            )

            Result.success(user)
        } catch (e: Exception) {
            Log.e("AuthRepository", "Login failed: ${e.message}")
            Result.failure(e)
        }
    }

    override suspend fun logout(): Result<Unit> {
        return try {
            firebaseAuth.signOut()
            userDao.deleteUser(userDao.getCurrentUser() ?: return Result.success(Unit))
            Result.success(Unit)
        } catch (e: Exception) {
            Log.e("AuthRepository", "Logout failed: ${e.message}")
            Result.failure(e)
        }
    }

    override suspend fun getCurrentUser(): Result<User?> {
        return try {
            val firebaseUser = firebaseAuth.currentUser
            if (firebaseUser != null) {
                val user = User(
                    id = firebaseUser.uid,
                    email = firebaseUser.email ?: "",
                    displayName = firebaseUser.displayName,
                    role = "Contractor"
                )
                Result.success(user)
            } else {
                Result.success(null)
            }
        } catch (e: Exception) {
            Log.e("AuthRepository", "Get current user failed: ${e.message}")
            Result.failure(e)
        }
    }

    override suspend fun isLoggedIn(): Boolean {
        return firebaseAuth.currentUser != null
    }
}
