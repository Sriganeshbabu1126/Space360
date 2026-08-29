# Space360 Android — Phase 2 Feature B: Offline Sync + Local Caching
## AG Prompt (Ready to Execute)

**Target:** Build production-ready offline-first caching layer + sync queue for Space360 Android app  
**Scope:** Foundational feature enabling Features A & C  
**Estimated duration:** 1–2 weeks  
**Dependencies:** Phase 1 (Auth, Navigation, Repository pattern) complete ✅  

---

## Context

You are building **Space360**, a 360° field inspection platform for construction site management. This is a **production backend** (FastAPI + PostgreSQL on Cloud Run) + **web app** (React + TypeScript, stages 1–2 complete) + **new native Android module** (this chat).

**Phase 1 (Android)** is complete:
- Auth: Firebase ID token login + persistence
- Dashboard + Issue Viewer skeleton
- Data layer: Retrofit API client + OkHttp interceptor
- Domain layer: Repository pattern (abstraction for network vs cache)
- Presentation layer: Jetpack Compose UI + ViewModels

**Phase 2 Feature B (NOW):** Implement offline-first architecture enabling field workers to:
- Use the app offline (read cached data)
- Queue writes (status updates, comments, photo uploads)
- Auto-sync when reconnected
- See sync status + manually retry failed ops

---

## Architecture Overview

### Offline-First Design Principles

1. **Cache-First Reads:** On app launch, fetch issues/sites from backend → store in Room → serve from Room (unless cache expired)
2. **Optimistic Writes:** User updates status offline → write to local queue + UI immediately → sync to server when reconnected
3. **Transparent Sync:** WorkManager background task flushes queue every 15 minutes + on reconnect
4. **Conflict Resolution:** Last-write-wins (simpler; if remote changed while user was offline, user's local change overwrites on sync)
5. **No User Friction:** Offline mode is transparent; user sees "Offline" banner + sync indicators, nothing else

### Data Flow

```
┌─────────────┐
│   Network   │
└──────┬──────┘
       │ (online)
       ▼
┌─────────────────────────┐
│   Repository (Smart)    │  ← Routes API vs Cache
├─────────────────────────┤
│ - Fetch w/ fallback     │
│ - Write to Queue        │
│ - Expire cache on sync  │
└──────┬──────┬───────────┘
       │      │
       ▼      ▼
    ┌──────────────┐     ┌────────────────┐
    │ Retrofit     │     │ Room (Local)   │
    │ (Network)    │     ├────────────────┤
    └──────────────┘     │ - issues       │
                         │ - comments     │
                         │ - sites        │
                         │ - sync_queue   │ ← NEW
                         │ - cache_meta   │ ← NEW
                         └────────────────┘

User → ViewModel → Repository → Room (cache) / Retrofit (network)
                ↓
          WorkManager → Sync Queue Flusher
                ↓
          Network (POST /issues/{id} → update cache)
```

---

## Room Schema Changes

### New Tables (Add to your existing `com.sgbdevapps.space360.data.local.database.AppDatabase`)

#### 1. `SyncQueueEntity` — Pending Write Operations

```kotlin
package com.sgbdevapps.space360.data.local.entities

import androidx.room.*
import java.time.Instant

@Entity(
    tableName = "sync_queue",
    indices = [
        Index("issueId"),
        Index("createdAt"),
        Index("syncedAt")
    ]
)
data class SyncQueueEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    val operationType: String, // "UPDATE_ISSUE_STATUS", "ADD_COMMENT", "ADD_PHOTO"
    val issueId: String,       // Which issue this op targets
    val payload: String,        // JSON serialized (see below for structure per operation type)
    
    val createdAt: Long,        // When queued (millis epoch)
    val syncedAt: Long? = null, // When successfully synced (null = not synced)
    
    val retryCount: Int = 0,
    val maxRetries: Int = 5,
    val lastError: String? = null,
    val lastErrorAt: Long? = null,
    
    val status: String = "PENDING" // "PENDING", "SYNCING", "SYNCED", "FAILED"
)

// Payload structures (JSON strings):
// {
//   "operationType": "UPDATE_ISSUE_STATUS",
//   "newStatus": "In Progress",
//   "userId": "contractor_123"
// }
//
// {
//   "operationType": "ADD_COMMENT",
//   "text": "Fixed the issue",
//   "userId": "contractor_123"
// }
//
// {
//   "operationType": "ADD_PHOTO",
//   "base64Data": "iVBORw0KGgo...",  // Base64 encoded image
//   "fileName": "photo_123.jpg"
// }
```

#### 2. `CacheMetadataEntity` — Cache Invalidation Tracking

```kotlin
@Entity(
    tableName = "cache_metadata",
    indices = [Index("entityType"), Index("expiresAt")]
)
data class CacheMetadataEntity(
    @PrimaryKey
    val cacheKey: String, // e.g., "issues:contractor_123:site_123", "sites:all"
    
    val entityType: String,    // "ISSUES", "SITES", "COMMENTS"
    val lastFetchedAt: Long,   // When data was last fetched from network (millis epoch)
    val expiresAt: Long,       // When cache expires (lastFetchedAt + TTL)
    val recordCount: Int = 0   // How many entities in this cache (debug info)
)
```

#### 3. `SiteEntity` — Contractor's Assigned Sites (NEW)

```kotlin
@Entity(
    tableName = "sites",
    indices = [Index("createdAt")]
)
data class SiteEntity(
    @PrimaryKey
    val id: String,
    
    val name: String,
    val location: String,
    val createdAt: Long
)
```

### Update Existing Entities (Add foreignKey constraints for data integrity)

```kotlin
// IssueEntity — Add index for offline queries
@Entity(
    tableName = "issues",
    indices = [
        Index("siteId"),
        Index("assignedTo"),
        Index("status"),
        Index("updatedAt")
    ],
    foreignKeys = [
        ForeignKey(
            entity = SiteEntity::class,
            parentColumns = ["id"],
            childColumns = ["siteId"],
            onDelete = ForeignKey.CASCADE
        )
    ]
)
data class IssueEntity(
    @PrimaryKey
    val id: String,
    val siteId: String,
    val title: String,
    val description: String,
    val status: String,
    val priority: String,
    val createdAt: Long,
    val updatedAt: Long,
    val assignedTo: String
)

// Add DAOs for new entities
```

### Room DAO Changes

```kotlin
// Add these to your existing DAOs or create new ones

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
    fun observePendingCount(): Flow<Int>
    
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

@Dao
interface SiteDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSites(sites: List<SiteEntity>)
    
    @Query("SELECT * FROM sites ORDER BY name ASC")
    fun getAllSites(): Flow<List<SiteEntity>>
    
    @Query("DELETE FROM sites")
    suspend fun deleteAllSites()
}
```

---

## Connectivity Detection

### Create `NetworkConnectivityManager` (New Class)

```kotlin
package com.sgbdevapps.space360.data.network

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.distinctUntilChanged
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NetworkConnectivityManager @Inject constructor(
    private val connectivityManager: ConnectivityManager
) {
    val isOnline: Flow<Boolean> = callbackFlow {
        val networkCallback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(true)
            }
            
            override fun onLost(network: Network) {
                trySend(false)
            }
            
            override fun onCapabilitiesChanged(
                network: Network,
                networkCapabilities: NetworkCapabilities
            ) {
                val hasInternet = networkCapabilities.hasCapability(
                    NetworkCapabilities.NET_CAPABILITY_INTERNET
                )
                trySend(hasInternet)
            }
        }
        
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
            .addTransportType(NetworkCapabilities.TRANSPORT_CELLULAR)
            .build()
        
        connectivityManager.registerNetworkCallback(request, networkCallback)
        
        // Initial check
        val currentState = connectivityManager.activeNetwork != null
        trySend(currentState)
        
        awaitClose {
            connectivityManager.unregisterNetworkCallback(networkCallback)
        }
    }.distinctUntilChanged()
    
    suspend fun isConnected(): Boolean {
        return connectivityManager.activeNetwork != null
    }
}
```

### Add to AndroidManifest.xml

```xml
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
```

---

## Sync Queue & Repository Integration

### Update Repository to Handle Offline Writes

```kotlin
package com.sgbdevapps.space360.domain.repositories

import com.sgbdevapps.space360.data.local.database.AppDatabase
import com.sgbdevapps.space360.data.local.entities.*
import com.sgbdevapps.space360.data.network.*
import com.sgbdevapps.space360.data.remote.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class IssueRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: AppDatabase,
    private val networkConnectivity: NetworkConnectivityManager
) {
    private val issueDao = database.issueDao()
    private val syncQueueDao = database.syncQueueDao()
    private val cacheMetadataDao = database.cacheMetadataDao()
    
    companion object {
        private const val CACHE_KEY_ISSUES = "issues"
        private const val CACHE_TTL_ISSUES_MS = 24 * 60 * 60 * 1000L // 24 hours
    }
    
    /**
     * Fetch issues with offline fallback
     * Priority: Cache if valid → Network fetch → Cache (expired)
     */
    suspend fun getIssuesForContractor(
        contractorId: String,
        siteId: String? = null,
        forceRefresh: Boolean = false
    ): Result<List<IssueEntity>> = runCatching {
        val cacheKey = "issues:$contractorId:${siteId ?: "all"}"
        val now = System.currentTimeMillis()
        
        // Check cache validity
        val cachedMetadata = cacheMetadataDao.getMetadata(cacheKey)
        val cacheIsValid = cachedMetadata?.expiresAt?.let { it > now } ?: false
        
        if (cacheIsValid && !forceRefresh) {
            // Serve from cache
            return@runCatching issueDao.getIssuesForContractor(contractorId, siteId)
        }
        
        // Attempt network fetch
        if (networkConnectivity.isConnected()) {
            return@runCatching try {
                val response = apiService.getIssues(
                    assignedTo = contractorId,
                    siteId = siteId
                )
                
                // Store in cache
                issueDao.insertIssues(response.map { it.toEntity() })
                cacheMetadataDao.upsertMetadata(
                    CacheMetadataEntity(
                        cacheKey = cacheKey,
                        entityType = "ISSUES",
                        lastFetchedAt = now,
                        expiresAt = now + CACHE_TTL_ISSUES_MS,
                        recordCount = response.size
                    )
                )
                
                response.map { it.toEntity() }
            } catch (e: Exception) {
                // Network failed; fall back to stale cache if available
                val fallback = issueDao.getIssuesForContractor(contractorId, siteId)
                if (fallback.isNotEmpty()) {
                    fallback
                } else {
                    throw e
                }
            }
        } else {
            // Offline; serve cache (even if expired)
            issueDao.getIssuesForContractor(contractorId, siteId)
        }
    }
    
    /**
     * Update issue status (Offline-aware)
     * Writes to sync queue immediately; syncs on reconnect
     */
    suspend fun updateIssueStatus(
        issueId: String,
        newStatus: String,
        contractorId: String
    ): Result<Unit> = runCatching {
        val now = System.currentTimeMillis()
        
        // Optimistic update locally
        issueDao.updateIssueStatus(issueId, newStatus, now)
        
        // Queue for sync
        val payload = Json.encodeToString(
            mapOf(
                "operationType" to "UPDATE_ISSUE_STATUS",
                "issueId" to issueId,
                "newStatus" to newStatus,
                "userId" to contractorId,
                "timestamp" to now
            )
        )
        
        syncQueueDao.insertOperation(
            SyncQueueEntity(
                operationType = "UPDATE_ISSUE_STATUS",
                issueId = issueId,
                payload = payload,
                createdAt = now,
                status = "PENDING"
            )
        )
        
        // Attempt immediate sync if online
        if (networkConnectivity.isConnected()) {
            syncSingleOperation(issueId, "UPDATE_ISSUE_STATUS")
        }
    }
    
    /**
     * Add comment to issue (Offline-aware)
     */
    suspend fun addComment(
        issueId: String,
        text: String,
        contractorId: String
    ): Result<Unit> = runCatching {
        val now = System.currentTimeMillis()
        
        // Create local comment entity
        val commentEntity = IssueCommentEntity(
            id = "temp_${System.nanoTime()}",
            issueId = issueId,
            text = text,
            authorId = contractorId,
            createdAt = now,
            status = "PENDING"  // Add status field to track sync state
        )
        
        // Store locally
        database.commentDao().insertComment(commentEntity)
        
        // Queue for sync
        val payload = Json.encodeToString(
            mapOf(
                "operationType" to "ADD_COMMENT",
                "issueId" to issueId,
                "text" to text,
                "userId" to contractorId,
                "timestamp" to now
            )
        )
        
        syncQueueDao.insertOperation(
            SyncQueueEntity(
                operationType = "ADD_COMMENT",
                issueId = issueId,
                payload = payload,
                createdAt = now,
                status = "PENDING"
            )
        )
        
        if (networkConnectivity.isConnected()) {
            syncSingleOperation(issueId, "ADD_COMMENT")
        }
    }
    
    /**
     * Sync single operation (called by WorkManager or manual retry)
     */
    private suspend fun syncSingleOperation(
        issueId: String,
        operationType: String
    ): Boolean {
        return try {
            val ops = syncQueueDao.getPendingOperations()
                .filter { it.issueId == issueId && it.operationType == operationType }
            
            for (op in ops) {
                when (op.operationType) {
                    "UPDATE_ISSUE_STATUS" -> {
                        val data = Json.parseToJsonElement(op.payload).jsonObject
                        val newStatus = data["newStatus"]?.jsonPrimitive?.content ?: return false
                        
                        apiService.updateIssueStatus(
                            issueId,
                            UpdateIssueStatusRequest(newStatus)
                        )
                    }
                    "ADD_COMMENT" -> {
                        val data = Json.parseToJsonElement(op.payload).jsonObject
                        val text = data["text"]?.jsonPrimitive?.content ?: return false
                        
                        apiService.addComment(
                            issueId,
                            AddCommentRequest(text)
                        )
                    }
                    // Handle ADD_PHOTO, etc.
                }
                
                // Mark as synced
                syncQueueDao.updateOperation(
                    op.copy(
                        status = "SYNCED",
                        syncedAt = System.currentTimeMillis()
                    )
                )
            }
            true
        } catch (e: Exception) {
            handleSyncFailure(issueId, operationType, e)
            false
        }
    }
    
    /**
     * Handle sync failure (retry logic)
     */
    private suspend fun handleSyncFailure(
        issueId: String,
        operationType: String,
        error: Exception
    ) {
        val ops = syncQueueDao.getPendingOperations()
            .filter { it.issueId == issueId && it.operationType == operationType }
        
        for (op in ops) {
            val updatedOp = op.copy(
                retryCount = op.retryCount + 1,
                lastError = error.message,
                lastErrorAt = System.currentTimeMillis(),
                status = if (op.retryCount >= op.maxRetries) "FAILED" else "PENDING"
            )
            syncQueueDao.updateOperation(updatedOp)
        }
    }
    
    /**
     * Get pending sync operations count (for UI display)
     */
    fun observePendingSyncCount(): Flow<Int> {
        return syncQueueDao.observePendingCount()
    }
    
    /**
     * Get failed operations (for retry UI)
     */
    suspend fun getFailedOperations(): List<SyncQueueEntity> {
        return syncQueueDao.getFailedOperations()
    }
}
```

---

## WorkManager Integration

### Create `SyncWorker` (Background Job)

```kotlin
package com.sgbdevapps.space360.data.sync

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.*
import com.sgbdevapps.space360.data.local.database.AppDatabase
import com.sgbdevapps.space360.data.network.ApiService
import com.sgbdevapps.space360.data.network.NetworkConnectivityManager
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import kotlinx.coroutines.tasks.await
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.util.concurrent.TimeUnit

@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val database: AppDatabase,
    private val apiService: ApiService,
    private val networkConnectivity: NetworkConnectivityManager
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        // Check if online
        if (!networkConnectivity.isConnected()) {
            // Reschedule; don't fail
            return Result.retry()
        }
        
        return try {
            val syncQueueDao = database.syncQueueDao()
            val pendingOps = syncQueueDao.getPendingOperations()
            
            if (pendingOps.isEmpty()) {
                return Result.success()
            }
            
            var successCount = 0
            var failureCount = 0
            
            for (op in pendingOps) {
                try {
                    when (op.operationType) {
                        "UPDATE_ISSUE_STATUS" -> {
                            val data = Json.parseToJsonElement(op.payload).jsonObject
                            val issueId = data["issueId"]?.jsonPrimitive?.content ?: continue
                            val newStatus = data["newStatus"]?.jsonPrimitive?.content ?: continue
                            
                            apiService.updateIssueStatus(
                                issueId,
                                UpdateIssueStatusRequest(newStatus)
                            )
                            successCount++
                        }
                        "ADD_COMMENT" -> {
                            val data = Json.parseToJsonElement(op.payload).jsonObject
                            val issueId = data["issueId"]?.jsonPrimitive?.content ?: continue
                            val text = data["text"]?.jsonPrimitive?.content ?: continue
                            
                            apiService.addComment(issueId, AddCommentRequest(text))
                            successCount++
                        }
                        // Handle other operation types
                    }
                    
                    // Mark as synced
                    syncQueueDao.updateOperation(
                        op.copy(
                            status = "SYNCED",
                            syncedAt = System.currentTimeMillis()
                        )
                    )
                } catch (e: Exception) {
                    failureCount++
                    
                    // Update retry count
                    val updatedOp = op.copy(
                        retryCount = op.retryCount + 1,
                        lastError = e.message,
                        lastErrorAt = System.currentTimeMillis(),
                        status = if (op.retryCount >= op.maxRetries) "FAILED" else "PENDING"
                    )
                    syncQueueDao.updateOperation(updatedOp)
                }
            }
            
            // Clean up old synced operations (older than 7 days)
            val sevenDaysAgo = System.currentTimeMillis() - (7 * 24 * 60 * 60 * 1000)
            syncQueueDao.deleteOldSyncedOperations(sevenDaysAgo)
            
            Result.success()
        } catch (e: Exception) {
            // Retry on exception
            Result.retry()
        }
    }
    
    companion object {
        private const val SYNC_WORK_NAME = "space360_sync_queue"
        
        fun schedulePeriodicSync(context: Context) {
            val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
                15,  // 15 minutes
                TimeUnit.MINUTES
            ).build()
            
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                SYNC_WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                syncRequest
            )
        }
        
        fun triggerImmediateSyncOnConnectivity(context: Context) {
            val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>().build()
            
            WorkManager.getInstance(context).enqueueUniqueWork(
                "${SYNC_WORK_NAME}_immediate",
                ExistingWorkPolicy.REPLACE,
                syncRequest
            )
        }
    }
}
```

### Add to build.gradle.kts (dependencies)

```gradle
dependencies {
    // Existing...
    implementation("androidx.work:work-runtime-ktx:2.8.1")
    implementation("androidx.hilt:hilt-work:1.0.0")
    kapt("androidx.hilt:hilt-compiler:1.0.0")
}
```

---

## UI Components

### 1. Offline Banner (Persistent Top Bar)

```kotlin
package com.sgbdevapps.space360.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.flow.Flow

@Composable
fun OfflineBanner(
    isOnline: Boolean,
    pendingSyncCount: Int
) {
    if (!isOnline) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFFFF9800)), // Amber warning color
            color = Color(0xFFFF9800)
        ) {
            Row(
                modifier = Modifier
                    .padding(horizontal = 16.dp, vertical = 8.dp)
                    .height(40.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(16.dp),
                        strokeWidth = 2.dp,
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = if (pendingSyncCount > 0) {
                            "Offline — $pendingSyncCount pending"
                        } else {
                            "Offline"
                        },
                        color = Color.White,
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
        }
    }
}
```

### 2. Sync Status Badge (Per-Issue Card)

```kotlin
@Composable
fun IssueSyncStatusBadge(syncStatus: String?) {
    when (syncStatus) {
        "PENDING", "SYNCING" -> {
            Surface(
                shape = RoundedCornerShape(4.dp),
                color = Color(0xFFFFF3E0) // Light amber
            ) {
                Row(
                    modifier = Modifier.padding(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(12.dp),
                        strokeWidth = 1.dp,
                        color = Color(0xFFFF9800)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        "Syncing",
                        fontSize = 10.sp,
                        color = Color(0xFFFF9800)
                    )
                }
            }
        }
        "FAILED" -> {
            Surface(
                shape = RoundedCornerShape(4.dp),
                color = Color(0xFFFFEBEE) // Light red
            ) {
                Row(
                    modifier = Modifier.padding(6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        "Retry",
                        fontSize = 10.sp,
                        color = Color(0xFFF44336),
                        modifier = Modifier.clickable { /* Retry action */ }
                    )
                }
            }
        }
        "SYNCED" -> {
            // No badge needed; data is current
        }
    }
}
```

### 3. Update IssuesPage to Show Offline Banner + Sync Status

```kotlin
@Composable
fun IssuesPage(
    viewModel: IssueViewModel,
    onNavigateToDetail: (String) -> Unit
) {
    val issues by viewModel.issues.collectAsState()
    val isOnline by viewModel.isOnline.collectAsState(true)
    val pendingSyncCount by viewModel.pendingSyncCount.collectAsState(0)
    val isLoading by viewModel.isLoading.collectAsState()
    
    Column(modifier = Modifier.fillMaxSize()) {
        // Offline banner at top
        OfflineBanner(isOnline = isOnline, pendingSyncCount = pendingSyncCount)
        
        // Content
        when {
            isLoading -> {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            issues.isEmpty() -> {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("No issues assigned")
                }
            }
            else -> {
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(issues) { issue ->
                        IssueCard(
                            issue = issue,
                            syncStatus = issue.syncStatus, // Add this to IssueEntity
                            onRetrySync = { viewModel.retrySync(issue.id) },
                            onClick = { onNavigateToDetail(issue.id) }
                        )
                    }
                }
            }
        }
    }
}
```

---

## ViewModel Updates

### Update IssueViewModel to Expose Connectivity + Sync State

```kotlin
package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.network.NetworkConnectivityManager
import com.sgbdevapps.space360.domain.repositories.IssueRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class IssueViewModel @Inject constructor(
    private val issueRepository: IssueRepository,
    private val networkConnectivity: NetworkConnectivityManager,
    private val syncWorker: SyncWorker? = null
) : ViewModel() {
    
    private val _isOnline = MutableStateFlow(true)
    val isOnline: StateFlow<Boolean> = _isOnline.asStateFlow()
    
    private val _pendingSyncCount = MutableStateFlow(0)
    val pendingSyncCount: StateFlow<Int> = _pendingSyncCount.asStateFlow()
    
    private val _issues = MutableStateFlow<List<IssueEntity>>(emptyList())
    val issues: StateFlow<List<IssueEntity>> = _issues.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    init {
        // Observe connectivity
        viewModelScope.launch {
            networkConnectivity.isOnline.collect { online ->
                _isOnline.value = online
                if (online) {
                    // Trigger sync on reconnect
                    triggerSync()
                }
            }
        }
        
        // Observe pending sync count
        viewModelScope.launch {
            issueRepository.observePendingSyncCount().collect { count ->
                _pendingSyncCount.value = count
            }
        }
        
        loadIssues()
    }
    
    fun loadIssues(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = issueRepository.getIssuesForContractor(
                    contractorId = "current_user_id",
                    forceRefresh = forceRefresh
                )
                _issues.value = result.getOrNull() ?: emptyList()
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun updateIssueStatus(issueId: String, newStatus: String) {
        viewModelScope.launch {
            issueRepository.updateIssueStatus(
                issueId = issueId,
                newStatus = newStatus,
                contractorId = "current_user_id"
            )
            loadIssues()
        }
    }
    
    fun retrySync(issueId: String? = null) {
        viewModelScope.launch {
            if (issueId != null) {
                // Retry single issue
                SyncWorker.triggerImmediateSyncOnConnectivity(context)
            } else {
                // Trigger full sync
                SyncWorker.triggerImmediateSyncOnConnectivity(context)
            }
        }
    }
    
    private fun triggerSync() {
        // Can be called via WorkManager or manually
        SyncWorker.triggerImmediateSyncOnConnectivity(context)
    }
}
```

---

## Android Manifest Updates

```xml
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />

<application>
    <!-- Hilt and WorkManager will auto-initialize via ContentProvider; no manual init needed -->
</application>
```

---

## Alembic Migration (Backend — Optional but Recommended)

While Room schema changes are client-side only, consider adding these backend tables to track sync state server-side (useful for admin debugging):

```python
# alembic/versions/xxx_add_sync_tracking.py
def upgrade():
    op.create_table(
        'sync_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('operation_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),  # 'SUCCESS', 'FAILED'
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('user_id', 'created_at')
    )
```

---

## Testing Strategy

### Unit Tests (MockRepository, no network)

```kotlin
// Test sync queue insertion on offline write
@Test
fun testUpdateIssueStatusQueuesOnOffline() = runTest {
    // Mock networkConnectivity.isConnected() → false
    // Call updateIssueStatus()
    // Assert SyncQueueEntity inserted with status "PENDING"
}

// Test cache TTL expiration
@Test
fun testExpiredCacheRefetchesOnOnline() = runTest {
    // Insert CacheMetadataEntity with expiresAt = now - 1 hour
    // Call getIssues()
    // Assert API called (fresh fetch)
}

// Test retry backoff
@Test
fun testSyncRetryBackoffIncrementsCount() = runTest {
    // Insert SyncQueueEntity with retryCount = 0
    // Simulate sync failure
    // Assert retryCount incremented
    // Assert status = "FAILED" after maxRetries exceeded
}
```

### Integration Tests (Real Room + Mock API)

```kotlin
// Test full offline → sync → refresh cycle
@Test
fun testOfflineSyncWorkflow() = runTest {
    // 1. Go offline
    // 2. Update issue status → verify queued
    // 3. Reconnect
    // 4. WorkManager executes sync
    // 5. Verify operation marked "SYNCED"
}
```

### Manual E2E Testing

1. **Login** → issues list loads + caches
2. **Kill network** → offline banner appears
3. **Update status** → see pending badge + syncing indicator
4. **Reconnect** → banner disappears, syncing completes
5. **Force quit app** → reopen → verify queue persisted
6. **Reach max retries** → see failed badge + manual retry button

---

## Summary of Deliverables

✅ **Room Schema** — 3 new tables (sync_queue, cache_metadata, sites) + updated DAOs  
✅ **NetworkConnectivityManager** — Observe online/offline state via Flow  
✅ **IssueRepository** — Offline-aware reads + write queuing  
✅ **SyncWorker** — Background job (15-min periodic + on-demand)  
✅ **UI Components** — Offline banner + sync status badges  
✅ **ViewModel Integration** — Expose isOnline + pendingSyncCount  
✅ **Error Handling** — Retry logic (exponential backoff, max 5 retries)  
✅ **Testing Strategy** — Unit + integration + E2E approach  

---

## Success Criteria (Phase 2 Feature B Complete)

- ✅ Offline banner visible when no network
- ✅ Writes queued immediately (optimistic local updates)
- ✅ WorkManager flushes queue every 15 min + on reconnect
- ✅ Synced operations marked in Room (syncedAt timestamp)
- ✅ Failed operations retry with backoff; max 5 retries → error badge
- ✅ Manual retry button on failed operations
- ✅ Cache expires per TTL (24h issues, 7d sites)
- ✅ Pull-to-refresh forces fresh network fetch
- ✅ No data loss if app force-quit mid-sync
- ✅ All tests passing (unit + integration)
- ✅ Zero crashes on actual SDK 26+ devices

---

## Notes for AG

1. **Kotlin serialization:** Use `kotlinx.serialization` (already in Phase 1 stack) for JSON encoding/decoding.
2. **Hilt wiring:** Ensure `NetworkConnectivityManager`, `AppDatabase`, `SyncWorker` are all injectable; use `@Singleton` / `@Inject` appropriately.
3. **Flow & StateFlow:** Leverage reactive patterns; avoid blocking calls in ViewModels.
4. **WorkManager Behavior:**
   - Respects doze mode on Android 6+
   - Auto-retries on process death
   - Survives app uninstall on some devices (edge case)
   - Test actual behavior on real device if possible
5. **Testing on Low-End Devices:** Min SDK 26 must not crash or ANR; test on emulator API 26.
6. **GCS Signed URL Caching:** When syncing photo uploads (Feature B doesn't include photos, Feature A does), ensure URLs refreshed if expired.

---

**Ready for AG. Send this prompt to AG + watch for code commits to `modules/android/` branch.**
