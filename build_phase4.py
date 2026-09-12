import os
import re

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path}")

# 1. OfflineSyncQueueEntity.kt
write_file("app/src/main/java/com/sgbdevapps/space360/data/local/OfflineSyncQueueEntity.kt", """
package com.sgbdevapps.space360.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "offline_sync_queue")
data class OfflineSyncQueueEntity(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    
    val action: String,
    val resourceType: String,
    val resourceId: String,
    val payload: String,
    
    val status: String = "pending",
    val attempts: Int = 0,
    val maxAttempts: Int = 5,
    val lastAttemptAt: Long? = null,
    val errorMessage: String? = null,
    
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
""")

# 2. OfflineSyncQueueDao.kt
write_file("app/src/main/java/com/sgbdevapps/space360/data/local/OfflineSyncQueueDao.kt", """
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
    
    @Update
    suspend fun update(item: OfflineSyncQueueEntity)
    
    @Query("DELETE FROM offline_sync_queue WHERE id = :id")
    suspend fun delete(id: String)
}
""")

# 3. OfflineSyncManager.kt
write_file("app/src/main/java/com/sgbdevapps/space360/service/OfflineSyncManager.kt", """
package com.sgbdevapps.space360.service

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.util.Log
import com.sgbdevapps.space360.data.local.Space360Database
import com.sgbdevapps.space360.data.remote.ApiService
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton
import com.sgbdevapps.space360.data.local.OfflineSyncQueueEntity
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import com.sgbdevapps.space360.data.remote.AddCommentRequest
import dagger.hilt.android.qualifiers.ApplicationContext

@Singleton
class OfflineSyncManager @Inject constructor(
    private val api: ApiService,
    private val db: Space360Database,
    @ApplicationContext private val context: Context
) {
    private val logger = "OfflineSyncManager"
    
    suspend fun queueAction(
        action: String,
        resourceType: String,
        resourceId: String,
        payload: Any
    ) {
        val jsonPayload = try {
            when (payload) {
                is UpdateIssueStatusRequest -> Json.encodeToString(payload)
                is AddCommentRequest -> Json.encodeToString(payload)
                else -> "{}"
            }
        } catch (e: Exception) { "{}" }
        
        val queueItem = OfflineSyncQueueEntity(
            action = action,
            resourceType = resourceType,
            resourceId = resourceId,
            payload = jsonPayload
        )
        db.offlineSyncQueueDao().insert(queueItem)
    }
    
    suspend fun syncPendingItems(): SyncResult {
        if (!isNetworkAvailable()) {
            return SyncResult(synced = 0, failed = 0, queued = 0)
        }
        
        val pendingItems = db.offlineSyncQueueDao().getPendingItems()
        var synced = 0
        var failed = 0
        
        for (item in pendingItems) {
            try {
                when (item.action) {
                    "update_status" -> {
                        val update = Json.decodeFromString<UpdateIssueStatusRequest>(item.payload)
                        api.updateIssueStatus(item.resourceId, update)
                    }
                    "add_comment" -> {
                        val comment = Json.decodeFromString<AddCommentRequest>(item.payload)
                        api.addComment(item.resourceId, comment)
                    }
                }
                
                item.copy(
                    status = "synced",
                    updatedAt = System.currentTimeMillis()
                ).let { db.offlineSyncQueueDao().update(it) }
                
                db.offlineSyncQueueDao().delete(item.id)
                synced++
                
            } catch (e: Exception) {
                Log.e(logger, "Sync failed for ${item.id}", e)
                item.copy(
                    status = if (item.attempts >= item.maxAttempts) "failed" else "pending",
                    attempts = item.attempts + 1,
                    lastAttemptAt = System.currentTimeMillis(),
                    errorMessage = e.message,
                    updatedAt = System.currentTimeMillis()
                ).let { db.offlineSyncQueueDao().update(it) }
                
                failed++
            }
        }
        
        return SyncResult(synced, failed, db.offlineSyncQueueDao().getPendingItems().size)
    }
    
    private fun isNetworkAvailable(): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}

data class SyncResult(
    val synced: Int,
    val failed: Int,
    val queued: Int
)
""")

# 4. SyncWorker.kt (Replacing the old one in worker package)
write_file("app/src/main/java/com/sgbdevapps/space360/worker/SyncWorker.kt", """
package com.sgbdevapps.space360.worker

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.*
import com.sgbdevapps.space360.service.OfflineSyncManager
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import java.util.concurrent.TimeUnit
import android.util.Log

@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val offlineSyncManager: OfflineSyncManager
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            val result = offlineSyncManager.syncPendingItems()
            
            if (result.failed > 0) {
                Log.w("SyncWorker", "Sync partial failure: ${result.synced} synced, ${result.failed} failed")
            } else if (result.queued > 0) {
                Log.i("SyncWorker", "Sync queued ${result.queued} items, will retry later")
            }
            
            Result.success()
        } catch (e: Exception) {
            Log.e("SyncWorker", "Sync worker failed", e)
            Result.retry()
        }
    }
    
    companion object {
        fun schedulePeriodicSync(context: Context) {
            val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
                15, TimeUnit.MINUTES
            ).setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                PeriodicWorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            ).build()
            
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "offline_sync",
                ExistingPeriodicWorkPolicy.KEEP,
                syncRequest
            )
        }
    }
}
""")

# 5. FirebaseMessagingService.kt
write_file("app/src/main/java/com/sgbdevapps/space360/service/FirebaseMessagingService.kt", """
package com.sgbdevapps.space360.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.sgbdevapps.space360.MainActivity
import com.sgbdevapps.space360.R
import com.sgbdevapps.space360.data.remote.ApiService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MyFirebaseMessagingService : FirebaseMessagingService() {
    
    @Inject lateinit var api: ApiService
    private val TAG = "FCMService"
    
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d(TAG, "New token: $token")
        // In real app, send this to backend.
        FirebaseMessaging.getInstance().subscribeToTopic("issues_all")
    }
    
    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        
        val title = message.notification?.title ?: "Space360"
        val body = message.notification?.body ?: "New notification"
        val issueId = message.data["issue_id"]
        
        sendNotification(title, body, issueId)
    }
    
    private fun sendNotification(title: String, body: String, issueId: String?) {
        val intent = Intent(this, MainActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
            putExtra("issue_id", issueId)
        }
        
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notificationBuilder = NotificationCompat.Builder(this, "issues")
            .setSmallIcon(R.mipmap.ic_launcher) // Fallback icon
            .setContentTitle(title)
            .setContentText(body)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
        
        try {
            if (androidx.core.app.ActivityCompat.checkSelfPermission(this, android.Manifest.permission.POST_NOTIFICATIONS) == android.content.pm.PackageManager.PERMISSION_GRANTED) {
                NotificationManagerCompat.from(this).notify(System.currentTimeMillis().toInt(), notificationBuilder.build())
            }
        } catch (e: Exception) { Log.e(TAG, "Notification error", e) }
    }
}
""")

# 6. IssueViewModel.kt (Renaming IssuesListViewModel)
write_file("app/src/main/java/com/sgbdevapps/space360/presentation/viewmodels/IssueViewModel.kt", """
package com.sgbdevapps.space360.presentation.viewmodels

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.data.remote.ApiService
import com.sgbdevapps.space360.data.remote.UpdateIssueStatusRequest
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.domain.model.Site
import com.sgbdevapps.space360.service.OfflineSyncManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class SyncStatus {
    IDLE, SYNCING, SYNCED, QUEUED, FAILED
}

@HiltViewModel
class IssueViewModel @Inject constructor(
    private val api: ApiService,
    private val offlineSyncManager: OfflineSyncManager
) : ViewModel() {
    
    private val TAG = "IssueViewModel"
    
    private val _issues = MutableStateFlow<List<Issue>>(emptyList())
    val issues = _issues.asStateFlow()
    
    private val _syncStatus = MutableStateFlow(SyncStatus.IDLE)
    val syncStatus = _syncStatus.asStateFlow()
    
    private val _selectedSite = MutableStateFlow<Site?>(null)
    val selectedSite = _selectedSite.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading = _isLoading.asStateFlow()
    
    fun loadIssues(siteId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val issuesList = api.getIssuesBySite(siteId = siteId)
                val mapped = issuesList.map { 
                    Issue(
                        id = it.id,
                        title = it.title,
                        description = it.description,
                        status = it.status,
                        priority = it.priority,
                        siteId = it.siteId,
                        createdAt = it.createdAt,
                        updatedAt = it.updatedAt,
                        comments = emptyList() // simplified
                    )
                }
                _issues.value = mapped
            } catch (e: Exception) {
                Log.e(TAG, "Failed to load issues", e)
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun updateIssueStatus(issueId: String, newStatus: String) {
        viewModelScope.launch {
            try {
                _syncStatus.value = SyncStatus.SYNCING
                api.updateIssueStatus(issueId, UpdateIssueStatusRequest(newStatus))
                _issues.value = _issues.value.map {
                    if (it.id == issueId) it.copy(status = newStatus) else it
                }
                _syncStatus.value = SyncStatus.SYNCED
            } catch (e: Exception) {
                Log.e(TAG, "Failed to update status", e)
                offlineSyncManager.queueAction(
                    action = "update_status",
                    resourceType = "issue",
                    resourceId = issueId,
                    payload = UpdateIssueStatusRequest(newStatus)
                )
                _syncStatus.value = SyncStatus.QUEUED
                
                // Optimistic UI update
                _issues.value = _issues.value.map {
                    if (it.id == issueId) it.copy(status = newStatus) else it
                }
            }
        }
    }
}
""")

# 7. IssuesScreen.kt (Replacing IssuesListScreen)
write_file("app/src/main/java/com/sgbdevapps/space360/presentation/screens/IssuesScreen.kt", """
package com.sgbdevapps.space360.presentation.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.sgbdevapps.space360.domain.model.Issue
import com.sgbdevapps.space360.presentation.viewmodels.IssueViewModel
import com.sgbdevapps.space360.presentation.viewmodels.SyncStatus
import androidx.navigation.NavController
import com.sgbdevapps.space360.presentation.components.StatusBadge

@Composable
fun IssuesScreen(
    navController: NavController,
    siteId: String,
    viewModel: IssueViewModel = hiltViewModel()
) {
    val issues by viewModel.issues.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val syncBadge by viewModel.syncStatus.collectAsState()
    
    LaunchedEffect(siteId) {
        viewModel.loadIssues(siteId)
    }
    
    Column(modifier = Modifier.fillMaxSize()) {
        if (syncBadge != SyncStatus.IDLE) {
            SyncStatusBadge(syncBadge)
        }
        
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (issues.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No issues yet")
            }
        } else {
            LazyColumn(modifier = Modifier.fillMaxSize()) {
                items(issues) { issue ->
                    IssueCardPhase4(
                        issue = issue,
                        onClick = { navController.navigate("issue/${issue.id}") },
                        onQuickStatusUpdate = { newStatus ->
                            viewModel.updateIssueStatus(issue.id, newStatus)
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun IssueCardPhase4(
    issue: Issue,
    onClick: () -> Unit,
    onQuickStatusUpdate: (String) -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    issue.title,
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.weight(1f)
                )
                StatusBadge(issue.status)
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(issue.description, maxLines = 2, overflow = TextOverflow.Ellipsis)
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("${issue.comments.size} comments", style = MaterialTheme.typography.bodySmall)
                
                Button(onClick = { onQuickStatusUpdate("in_review") }, modifier = Modifier.height(32.dp)) {
                    Text("Mark Review", fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
fun SyncStatusBadge(status: SyncStatus) {
    Surface(
        color = when (status) {
            SyncStatus.SYNCING -> Color.Yellow
            SyncStatus.SYNCED -> Color.Green
            SyncStatus.FAILED -> Color.Red
            else -> Color.Gray
        },
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            when (status) {
                SyncStatus.SYNCING -> {
                    CircularProgressIndicator(modifier = Modifier.size(20.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Syncing...")
                }
                SyncStatus.SYNCED -> Text("✓ Synced")
                SyncStatus.FAILED -> Text("✗ Sync failed - tap to retry")
                SyncStatus.QUEUED -> Text("↻ Queued for sync")
                else -> {}
            }
        }
    }
}
""")

print("Successfully wrote Phase 4a scripts")
