package com.sgbdevapps.space360.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface PathDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPath(path: PathEntity)

    @Query("SELECT * FROM paths WHERE id = :id")
    suspend fun getPathById(id: String): PathEntity?

    @Query("SELECT * FROM paths WHERE status = 'COMPLETED'")
    suspend fun getCompletedPaths(): List<PathEntity>

    @Query("UPDATE paths SET status = :status, uploadedAt = :uploadedAt WHERE id = :id")
    suspend fun updatePathStatus(id: String, status: String, uploadedAt: Long?)
    
    @Query("SELECT * FROM paths WHERE siteId = :siteId ORDER BY startedAt DESC")
    fun observePathsForSite(siteId: String): Flow<List<PathEntity>>
}

@Dao
interface PathPointDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPathPoint(point: PathPointEntity)

    @Query("SELECT * FROM path_points WHERE pathId = :pathId ORDER BY timestamp ASC")
    suspend fun getPointsForPath(pathId: String): List<PathPointEntity>
    
    @Query("SELECT COUNT(*) FROM path_points WHERE pathId = :pathId")
    fun observeWaypointCount(pathId: String): Flow<Int>
}
