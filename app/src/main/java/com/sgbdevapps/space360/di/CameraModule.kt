package com.sgbdevapps.space360.di

import android.content.Context
import com.sgbdevapps.space360.domain.repository.PathRepository
import com.sgbdevapps.space360.service.Insta360Controller
import com.sgbdevapps.space360.service.Insta360SyncManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object CameraModule {
    
    @Provides
    @Singleton
    fun provideInsta360Controller(@ApplicationContext context: Context): Insta360Controller {
        return Insta360Controller(context)
    }
    
    @Provides
    @Singleton
    fun provideInsta360SyncManager(
        controller: Insta360Controller,
        pathRepository: PathRepository,
        @ApplicationContext context: Context
    ): Insta360SyncManager {
        return Insta360SyncManager(controller, pathRepository, context)
    }
}
