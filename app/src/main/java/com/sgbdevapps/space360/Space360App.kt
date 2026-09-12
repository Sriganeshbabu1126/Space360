package com.sgbdevapps.space360

import android.app.Application
import androidx.hilt.work.HiltWorkerFactory
import androidx.work.Configuration
import com.google.firebase.Firebase
import com.google.firebase.crashlytics.crashlytics
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

@HiltAndroidApp
class Space360App : Application(), Configuration.Provider {
    @Inject
    lateinit var workerFactory: HiltWorkerFactory

    override fun getWorkManagerConfiguration(): Configuration =
        Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()
            
    override fun onCreate() {
        super.onCreate()
        
        // Initialize Firebase Crashlytics
        com.google.firebase.Firebase.crashlytics.apply {
            setCrashlyticsCollectionEnabled(true)
            setCustomKey("app_version", BuildConfig.VERSION_NAME)
            setCustomKey("build_type", BuildConfig.BUILD_TYPE)
        }
        
        // Set global uncaught exception handler
        val defaultHandler = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            android.util.Log.e("Space360App", "Uncaught exception in thread: ${thread.name}", throwable)
            com.google.firebase.Firebase.crashlytics.recordException(throwable)
            defaultHandler?.uncaughtException(thread, throwable)
        }
        
        com.sgbdevapps.space360.data.sync.SyncWorker.schedulePeriodicSync(this)
    }
}
