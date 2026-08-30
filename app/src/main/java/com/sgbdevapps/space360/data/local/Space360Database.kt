package com.sgbdevapps.space360.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [
        UserEntity::class,
        SiteEntity::class,
        IssueEntity::class,
        IssueCommentEntity::class,
        IssuePhotoEntity::class,
        SyncQueueEntity::class,
        CacheMetadataEntity::class
    ],
    version = 4
)
abstract class Space360Database : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun siteDao(): SiteDao
    abstract fun issueDao(): IssueDao
    abstract fun issueCommentDao(): IssueCommentDao
    abstract fun issuePhotoDao(): IssuePhotoDao
    abstract fun syncQueueDao(): SyncQueueDao
    abstract fun cacheMetadataDao(): CacheMetadataDao
}
