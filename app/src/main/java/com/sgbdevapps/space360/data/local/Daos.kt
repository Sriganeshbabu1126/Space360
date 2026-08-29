package com.sgbdevapps.space360.data.local

import androidx.room.*

@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUserById(id: Int): UserEntity?

    @Query("SELECT * FROM users LIMIT 1")
    suspend fun getCurrentUser(): UserEntity?

    @Delete
    suspend fun deleteUser(user: UserEntity)
}

@Dao
interface SiteDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSites(sites: List<SiteEntity>)

    @Query("SELECT * FROM sites")
    suspend fun getAllSites(): List<SiteEntity>

    @Query("SELECT * FROM sites WHERE id = :id")
    suspend fun getSiteById(id: Int): SiteEntity?

    @Query("DELETE FROM sites")
    suspend fun deleteAllSites()
}

@Dao
interface IssueDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertIssues(issues: List<IssueEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertIssue(issue: IssueEntity)

    @Query("SELECT * FROM issues WHERE siteId = :siteId")
    suspend fun getIssuesBySite(siteId: Int): List<IssueEntity>

    @Query("SELECT * FROM issues WHERE id = :id")
    suspend fun getIssueById(id: Int): IssueEntity?

    @Query("DELETE FROM issues WHERE siteId = :siteId")
    suspend fun deleteIssuesBySite(siteId: Int)
}

@Dao
interface IssueCommentDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertComments(comments: List<IssueCommentEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertComment(comment: IssueCommentEntity)

    @Query("SELECT * FROM issue_comments WHERE issueId = :issueId ORDER BY createdAt ASC")
    suspend fun getCommentsByIssue(issueId: Int): List<IssueCommentEntity>

    @Query("DELETE FROM issue_comments WHERE issueId = :issueId")
    suspend fun deleteCommentsByIssue(issueId: Int)
}

@Dao
interface IssuePhotoDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPhotos(photos: List<IssuePhotoEntity>)

    @Query("SELECT * FROM issue_photos WHERE issueId = :issueId")
    suspend fun getPhotosByIssue(issueId: Int): List<IssuePhotoEntity>

    @Query("DELETE FROM issue_photos WHERE issueId = :issueId")
    suspend fun deletePhotosByIssue(issueId: Int)
}

@Dao
interface SyncQueueDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOperation(op: SyncQueueEntity)
    
    @Query("SELECT * FROM sync_queue WHERE status = 'PENDING' ORDER BY createdAt ASC")
    suspend fun getPendingOperations(): List<SyncQueueEntity>
    
    @Query("SELECT * FROM sync_queue WHERE status = 'FAILED' ORDER BY createdAt DESC LIMIT 50")
    suspend fun getFailedOperations(): List<SyncQueueEntity>
    
    @Update
    suspend fun updateOperation(op: SyncQueueEntity)
    
    @Delete
    suspend fun deleteOperation(op: SyncQueueEntity)
    
    @Query("SELECT COUNT(*) FROM sync_queue WHERE status = 'PENDING'")
    fun observePendingCount(): kotlinx.coroutines.flow.Flow<Int>
    
    @Query("DELETE FROM sync_queue WHERE syncedAt IS NOT NULL AND syncedAt < :cutoffTime")
    suspend fun deleteOldSyncedOperations(cutoffTime: Long)
}

@Dao
interface CacheMetadataDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertMetadata(meta: CacheMetadataEntity)
    
    @Query("SELECT * FROM cache_metadata WHERE cacheKey = :key")
    suspend fun getMetadata(key: String): CacheMetadataEntity?
    
    @Query("DELETE FROM cache_metadata WHERE expiresAt < :now")
    suspend fun deleteExpiredMetadata(now: Long)
    
    @Query("SELECT COUNT(*) FROM cache_metadata WHERE entityType = :type AND expiresAt > :now")
    suspend fun hasValidCache(type: String, now: Long): Int
}
