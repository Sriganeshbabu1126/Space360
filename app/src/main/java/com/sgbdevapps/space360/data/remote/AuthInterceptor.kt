package com.sgbdevapps.space360.data.remote

import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import com.google.android.gms.tasks.Tasks

class AuthInterceptor @Inject constructor(
    private val firebaseAuth: FirebaseAuth
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        val idToken = try {
            val user = firebaseAuth.currentUser
            if (user != null) {
                Log.d("AuthInterceptor", "Fetching token for URL: ${originalRequest.url}")
                val task = user.getIdToken(false)
                val token = Tasks.await(task).token ?: ""
                Log.d("AuthInterceptor", "Token fetched successfully. Length: ${token.length}")
                token
            } else {
                Log.e("AuthInterceptor", "User is NULL in AuthInterceptor for URL: ${originalRequest.url}")
                ""
            }
        } catch (e: Exception) {
            Log.e("AuthInterceptor", "Failed to get token for URL: ${originalRequest.url}", e)
            ""
        }

        val requestWithToken = originalRequest.newBuilder()
            .header("Authorization", "Bearer $idToken")
            .build()
            
        Log.d("AuthInterceptor", "Proceeding with Auth header: Bearer ${if (idToken.isNotEmpty()) "[HIDDEN]" else "[EMPTY]"}")

        var response = chain.proceed(requestWithToken)

        if (response.code == 401) {
            Log.e("AuthInterceptor", "Unauthorized (401) on ${originalRequest.url}. Forcing token refresh...")
            response.close() 
            
            val refreshedToken = try {
                val user = firebaseAuth.currentUser
                if (user != null) {
                    val task = user.getIdToken(true) // FORCE REFRESH
                    val token = Tasks.await(task).token ?: ""
                    Log.d("AuthInterceptor", "Forced refresh successful. Length: ${token.length}")
                    token
                } else {
                    ""
                }
            } catch (e: Exception) {
                Log.e("AuthInterceptor", "Failed to force refresh token", e)
                ""
            }
            
            if (refreshedToken.isNotEmpty()) {
                val retryRequest = originalRequest.newBuilder()
                    .header("Authorization", "Bearer $refreshedToken")
                    .build()
                response = chain.proceed(retryRequest)
            }
            
            if (response.code == 401) {
                Log.e("AuthInterceptor", "Still 401 after refresh. Preserving session...")
            }
        }

        return response
    }

}

