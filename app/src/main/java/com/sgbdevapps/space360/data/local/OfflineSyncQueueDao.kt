package com.sgbdevapps.space360.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update

@Dao
interface OfflineSyncQueueDao {
    @Insert
    suspend fun insert(item: OfflineSyncQueueEntity)
    
    @Query("SELECT * FROM offline_sync_queue WHERE status = 'pending' ORDER BY createdAt ASC LIMIT 50")
    suspend fun getPendingItems(): List<OfflineSyncQueueEntity>
    
    @Query("SELECT * FROM offline_sync_queue WHERE status = 'pending' AND resourceType = :resourceType AND resourceId = :resourceId ORDER BY createdAt ASC")
    suspend fun getPendingItemsForResource(resourceType: String, resourceId: String): List<OfflineSyncQueueEntity>
    
    @Update
    suspend fun update(item: OfflineSyncQueueEntity)
    
    @Query("DELETE FROM offline_sync_queue WHERE id = :id")
    suspend fun delete(id: String)
}
