package com.sgbdevapps.space360.data.remote

import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

import com.google.android.gms.tasks.Tasks

class AuthInterceptor @Inject constructor(
    private val firebaseAuth: FirebaseAuth
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        // Get Firebase ID token synchronously
        val idToken = try {
            val user = firebaseAuth.currentUser
            if (user != null) {
                val task = user.getIdToken(false)
                Tasks.await(task).token ?: ""
            } else {
                ""
            }
        } catch (e: Exception) {
            Log.e("AuthInterceptor", "Failed to get token", e)
            ""
        }

        // Inject Bearer token
        val requestWithToken = originalRequest.newBuilder()
            .header("Authorization", "Bearer $idToken")
            .build()

        val response = chain.proceed(requestWithToken)

        // On 401, logout
        if (response.code == 401) {
            Log.e("AuthInterceptor", "Unauthorized (401) — logging out")
            firebaseAuth.signOut()
            // TODO: Notify ViewModels of logout (use EventBus or StateFlow)
        }

        return response
    }
}
