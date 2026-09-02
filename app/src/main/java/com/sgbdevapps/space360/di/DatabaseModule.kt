package com.sgbdevapps.space360.di

import android.content.Context
import androidx.room.Room
import com.sgbdevapps.space360.data.local.Space360Database
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideSpace360Database(@ApplicationContext context: Context): Space360Database {
        return Room.databaseBuilder(
            context,
            Space360Database::class.java,
            "space360_db"
        )
        .fallbackToDestructiveMigration()
        .build()
    }

    @Provides
    fun provideUserDao(database: Space360Database) = database.userDao()

    @Provides
    fun provideSiteDao(database: Space360Database) = database.siteDao()

    @Provides
    fun provideIssueDao(database: Space360Database) = database.issueDao()

    @Provides
    fun provideIssueCommentDao(database: Space360Database) = database.issueCommentDao()

    @Provides
    fun provideIssuePhotoDao(database: Space360Database) = database.issuePhotoDao()

    @Provides
    fun provideSyncQueueDao(database: Space360Database) = database.syncQueueDao()

    @Provides
    fun provideCacheMetadataDao(database: Space360Database) = database.cacheMetadataDao()

    @Provides
    fun providePathDao(database: Space360Database) = database.pathDao()

    @Provides
    fun providePathPointDao(database: Space360Database) = database.pathPointDao()
}
