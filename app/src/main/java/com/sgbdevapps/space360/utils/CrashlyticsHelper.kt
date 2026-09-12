package com.sgbdevapps.space360.utils

import com.google.firebase.Firebase
import com.google.firebase.crashlytics.crashlytics
import android.util.Log

object CrashlyticsHelper {
    private const val TAG = "CrashlyticsHelper"
    
    fun logEvent(message: String) {
        Log.d(TAG, "CrashlyticsEvent: $message")
        Firebase.crashlytics.log(message)
    }
    
    fun logError(message: String, throwable: Throwable? = null) {
        Log.e(TAG, message, throwable)
        Firebase.crashlytics.log("ERROR: $message")
        if (throwable != null) {
            Firebase.crashlytics.recordException(throwable)
        }
    }
    
    fun setUserContext(userId: String, email: String) {
        Firebase.crashlytics.apply {
            setUserId(userId)
            setCustomKey("user_email", email)
            log("User context set: $email")
        }
    }
    
    fun clearUserContext() {
        Firebase.crashlytics.setUserId("")
    }
    
    fun setCustomData(key: String, value: String) {
        Firebase.crashlytics.setCustomKey(key, value)
    }
}
