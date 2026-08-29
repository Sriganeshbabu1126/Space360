# Space360 Android — Phase 2 Feature A: Issue Viewer
## AG Prompt (Ready to Execute)

**Target:** Build contractor-facing Issue Viewer with full CRUD (read + update status + comment + photo upload)  
**Scope:** Core mobile UX enabling field workers to manage assigned issues on-site  
**Estimated duration:** 2–3 weeks  
**Dependencies:** Phase 1 (Auth, Navigation, Repository) + Phase 2 Feature B (Offline Sync) COMPLETE ✅  

---

## Context

**Space360** is a 360° field inspection platform for construction sites. **Phase 2 Feature B** (Offline Sync + Local Caching) is now complete with:
- Room schema + sync queue
- NetworkConnectivityManager (online/offline detection)
- SyncWorker (15-min periodic sync + on-demand)
- IssueRepositoryImpl (offline-aware reads + write queueing)
- OfflineBanner + SyncStatusBadge UI
- IssuesListViewModel (exposes isOnline + pendingSyncCount)

**Phase 2 Feature A (NOW)** builds the full Issue Viewer UI/UX on top of Feature B, enabling contractors to:
- View assigned issues (list filtered by site + status + priority)
- View issue details (description, comments, photos, history)
- Update issue status (Open → In Progress → Done workflow)
- Add comments (text, synced via queue)
- Add photos as evidence (multi-select, upload, view in lightbox)
- Work offline (read cached data, queue writes, sync on reconnect)

---

## Architecture Overview

### Data Flow (Feature A Layers)

```
┌────────────────────────────────────────────────────────┐
│           Jetpack Compose UI Layer                      │
│  IssuesListScreen, IssueDetailScreen, PhotoGallery,    │
│  StatusUpdateBottomSheet, CommentInputField            │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│          ViewModels (State Management)                 │
│  IssuesListViewModel, IssueDetailViewModel             │
│  • Observe issues, detail, comments, photos            │
│  • Handle status updates, comments, photo uploads      │
│  • Observe isOnline (from Feature B)                   │
│  • Expose loading, error, pendingSyncCount states      │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│    Domain Layer (IssueRepository from Phase 1)         │
│  • getIssuesBySite() — offline-aware reads             │
│  • updateIssueStatus() — queue via Feature B           │
│  • addComment() — queue via Feature B                  │
│  • addPhotoToIssue() — upload + queue via Feature B    │
└────────────────────┬─────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   Retrofit (Network)      Room Cache (Feature B)
   • GET /issues           • issues table
   • GET /issues/{id}      • comments table
   • PUT /issues/{id}      • photos table
   • POST /comments        • sync_queue table
   • POST /photos          • cache_metadata
```

### Key Principles

1. **Offline-First:** All reads default to Room cache (Feature B). Network fetches populate cache. If offline, stale cache is acceptable.
2. **Optimistic Updates:** Status + comment changes update UI immediately; sync happens quietly in background (Feature B's SyncWorker).
3. **Photo Upload:** Multi-select JPG/PNG files → queue for sync → display thumbnail locally → sync to GCS → refresh URL on display.
4. **Contractor-Scoped:** All API calls respect contractor ID (JWT payload). Backend enforces RBAC on 401.
5. **Error Transparency:** Network errors show toasts; sync failures show badges + retry buttons.

---

## Screen Designs

### Screen 1: IssuesListScreen

**Purpose:** Display all issues assigned to contractor across all sites

**Layout:**
```
┌──────────────────────────────────────┐
│  [OfflineBanner - if offline]        │  ← Feature B component
├──────────────────────────────────────┤
│  [SearchBar + Filter Icon]           │  ← New (search + filters)
│  Filters: Status, Site, Priority     │
├──────────────────────────────────────┤
│ ┌────────────────────────────────┐  │
│ │ Issue Card #1                  │  │
│ │ ┌──────────────────────────┐  │  │
│ │ │ [Site Name] • Priority   │  │  │
│ │ │ Issue Title              │  │  │
│ │ │ Status: [Open] | Updated: 2h ago │ │
│ │ │ [Syncing badge] or [Retry btn]   │  │  ← Feature B
│ │ └──────────────────────────┘  │  │
│ │ 👆 Tap to open detail        │  │
│ └────────────────────────────────┘  │
│ ┌────────────────────────────────┐  │
│ │ Issue Card #2                  │  │
│ │ ... (scroll for more)          │  │
│ └────────────────────────────────┘  │
│                                      │
│ [Pull-to-refresh indicator]         │
└──────────────────────────────────────┘
```

**Components:**
- **SearchBar** (top): Quick text search across issue titles + descriptions
- **FilterButton**: Opens inline filter panel (Status dropdown, Site dropdown, Priority dropdown)
- **IssueCard** (repeating): 
  - Site name (badge)
  - Issue title (bold, truncated to 2 lines)
  - Brief description (gray, 1 line)
  - Status badge (color-coded: Open=blue, In Progress=amber, Done=green)
  - Updated timestamp (relative, e.g., "2h ago")
  - Sync status (from Feature B): yellow "Syncing" or red "Retry" badge
  - Tap to navigate to IssueDetailScreen
- **LazyColumn**: Infinite scroll or pagination
- **Pull-to-Refresh** (PullRefreshIndicator): Force fresh fetch, bypass cache TTL

**Behavior:**
- On screen load: 
  - Fetch issues from IssueRepository (offline-aware)
  - Show cached data immediately if available
  - If online and cache expired, fetch fresh
  - If offline, show cached (even if stale)
- On pull-to-refresh: Force fresh network fetch (bypass cache)
- On filter change: Re-filter in-memory (no new API call; filters applied client-side)
- On sync status change: Update badge in real-time (observe pendingSyncCount from Feature B)

**Acceptance Criteria:**
- ✅ List loads with contractor's issues only (backend enforces scope)
- ✅ Filters work (status, site, priority combinations)
- ✅ Search finds issues by title/description
- ✅ Pull-to-refresh forces fresh network fetch
- ✅ Offline: shows cached data
- ✅ Sync badges (yellow "Syncing" / red "Retry") appear + update
- ✅ Infinite scroll or pagination works (no UI freeze on large lists)
- ✅ Zero crashes on SDK 26

---

### Screen 2: IssueDetailScreen

**Purpose:** View full issue data (title, description, status, priority, comments, photos) + update status + add comments

**Layout:**
```
┌──────────────────────────────────────┐
│  [Back Button] [Issue Title]  [Menu]  │  ← Header
├──────────────────────────────────────┤
│  Site: [Site Name] | Priority: [High]│  ← Metadata
│  Status: [Open] • Created: 2d ago    │
├──────────────────────────────────────┤
│  Issue Description                   │
│  Lorem ipsum dolor sit amet...       │
│  (expandable if long)                │
├──────────────────────────────────────┤
│  📷 Evidence Photos (Photo Gallery)  │  ← NEW Feature A
│  ┌─────────┬─────────┬─────────┐    │
│  │ [Photo] │ [Photo] │ [Photo] │    │ (2–3 cols responsive)
│  ├─────────┼─────────┼─────────┤    │
│  │ [Photo] │ [Add+]  │         │    │  ← Add button for new photos
│  └─────────┴─────────┴─────────┘    │
│  Tap photo → Lightbox (swipe nav)    │
├──────────────────────────────────────┤
│  💬 Comments (Thread)                │
│  ┌────────────────────────────────┐ │
│  │ Contractor A — 2h ago          │ │
│  │ "Fixed the leak"               │ │
│  │                                │ │
│  │ Contractor B — 1h ago          │ │
│  │ "Verified. Good work!"         │ │
│  └────────────────────────────────┘ │
│  [Scroll for more comments]         │
├──────────────────────────────────────┤
│  [Status Update Card]                │  ← Bottom sheet trigger
│  Current: [Open] | Change to: [v]   │
│  ┌────────────────────────────────┐ │
│  │ RadioButton: In Progress       │ │
│  │ RadioButton: Done              │ │
│  │ [Cancel] [Update]              │ │
│  └────────────────────────────────┘ │
├──────────────────────────────────────┤
│  [CommentInputField]                 │  ← Add comment
│  [Input Box] [Send Button]          │
└──────────────────────────────────────┘
```

**Components:**

1. **Header Section:**
   - Back button (navigate to IssuesListScreen)
   - Issue title (bold, full text)
   - Menu button (options: refresh, delete attachment, etc. — TBD Phase 3)

2. **Metadata Section:**
   - Site name (clickable? → filters list to this site)
   - Priority badge (High=red, Medium=yellow, Low=gray)
   - Status badge (color-coded)
   - Created date, last updated date (relative timestamps)

3. **Description Section:**
   - Full issue description (may be long; truncate at ~200 chars, add "Read more" button for full text)

4. **Photo Gallery (NEW):**
   - Responsive grid (2–3 columns on phone, adjust for landscape)
   - Photo thumbnails loaded via Coil
   - Tap photo → open Lightbox
   - "+" button to add new photos → file picker (multi-select)
   - Photo count badge (e.g., "3 photos")
   - Metadata on hover/long-press (upload date, size, sync status)

5. **Lightbox (Fullscreen Photo Viewer):**
   - Full-size photo display
   - Swipe left/right to navigate between photos
   - Pinch-to-zoom
   - Double-tap to zoom
   - ESC / back button to close
   - Info bar showing current photo index (e.g., "Photo 2 of 3") + upload date
   - Share button (optional Phase 3)

6. **Comments Section:**
   - Chronological thread (oldest first, newest at bottom)
   - Each comment shows: author name, timestamp (relative), comment text
   - Left border or subtle background to visually group thread
   - Scroll within section if many comments
   - Pending comments show "pending" badge (gray, until synced)

7. **Status Update Card:**
   - Current status display
   - RadioButton group: "In Progress" (only if current = Open), "Done" (only if current = In Progress)
   - Constraint: Open → In Progress → Done (sequential; no skipping)
   - [Cancel] [Update] buttons
   - Shows as expandable bottom sheet OR inline (TBD — recommend inline for mobile UX)

8. **Comment Input Field:**
   - Text input box (placeholder: "Add a comment...")
   - Send button (paper-plane icon)
   - Disabled if offline (show hint: "Offline — comment queued when online")
   - Pending state: show spinner until API response
   - On success: clear input, add comment to thread with "pending" badge
   - On error: show error toast, keep input text, retry button

**Behavior:**
- On screen load:
  - Fetch issue detail from IssueRepository (offline-aware)
  - Display cached data immediately
  - Fetch fresh if online and cache expired
  - If offline, show stale cache (mark with "cached X hours ago" indicator)
- On photo upload:
  - File picker (allow multi-select, JPG/PNG only, max 5MB per file)
  - Show thumbnail immediately (local preview)
  - Queue upload via IssueRepository.addPhotoToIssue()
  - Show "pending" badge on thumbnail
  - On sync: refresh photo URL (GCS signed URL), remove pending badge
  - On sync failure: show error badge + retry button
- On status update:
  - Call IssueRepository.updateIssueStatus() → queued via Feature B
  - Update UI immediately (optimistic)
  - Show "syncing" badge until queued operation syncs
  - On sync: remove badge, status is now authoritative
- On comment add:
  - Call IssueRepository.addComment() → queued via Feature B
  - Add comment to thread immediately with "pending" badge
  - On sync: remove pending badge
  - On error: show error badge + retry button

**Acceptance Criteria:**
- ✅ Issue detail loads (title, description, status, priority, dates)
- ✅ Photo gallery displays all attached photos (responsive grid)
- ✅ Can add photos (multi-select, JPG/PNG, display preview, queue upload)
- ✅ Lightbox works (full-size, swipe, pinch-zoom, ESC closes)
- ✅ Comments display in chronological order with author + timestamp
- ✅ Can add comments (text input, send, appear immediately with "pending" badge)
- ✅ Status update works (Open → In Progress → Done, queued via Feature B)
- ✅ Offline: can read cached data, can't add comments/photos (disabled with hint)
- ✅ Sync badges appear (yellow "syncing" / red "retry") + update in real-time
- ✅ Zero crashes on SDK 26

---

### Screen 3: StatusUpdateBottomSheet (Modal)

**Purpose:** Provide clean interface for changing issue status

**Layout:**
```
┌──────────────────────────────────────┐
│  Change Issue Status                 │
├──────────────────────────────────────┤
│  Current status: [Open]              │
│                                      │
│  ☐ In Progress                       │  ← Only if current = Open
│  ☐ Done                              │  ← Only if current = In Progress
│                                      │
│  [Cancel]  [Update]                 │
└──────────────────────────────────────┘
```

**Components:**
- Title: "Change Issue Status"
- Current status indicator (read-only)
- RadioButton group (only valid transitions shown)
- [Cancel] button → dismiss sheet
- [Update] button → call updateIssueStatus() → dismiss sheet

**Logic:**
- Open → can transition to "In Progress"
- In Progress → can transition to "Done"
- Done → no transitions (read-only)
- Contractor role only (enforced by backend)

---

### Screen 4: CommentInputField (Reusable Component)

**Purpose:** Isolated component for adding comments, reused on IssueDetailScreen

**Layout:**
```
┌──────────────────────────────────────┐
│  [Text Input]              [Send ✈️]  │
└──────────────────────────────────────┘
```

**Components:**
- **TextField:** 
  - Placeholder: "Add a comment..."
  - Multiline (expand as user types)
  - Max 500 characters
  - Character counter (optional)
- **Send Button:**
  - Paper-plane icon
  - Disabled if text is empty
  - Disabled if offline (show disabled state)
  - Shows spinner while sending (optimistic)
- **Hint Text (if offline):**
  - "Offline — comment will be queued"

**Behavior:**
- On "Send" tap:
  - Call IssueRepository.addComment(issueId, text)
  - Clear input field
  - Show spinner
  - Add comment to thread with "pending" badge immediately
  - On sync success: remove pending badge
  - On sync failure: show error toast, add retry button to comment
- If offline:
  - Send button still works (queues locally)
  - Show hint: "Comment queued — will sync when online"

---

## ViewModel Specs

### IssueDetailViewModel

```kotlin
package com.sgbdevapps.space360.presentation.viewmodels

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sgbdevapps.space360.domain.models.Issue
import com.sgbdevapps.space360.domain.models.IssueComment
import com.sgbdevapps.space360.domain.models.IssuePhoto
import com.sgbdevapps.space360.domain.repositories.IssueRepository
import com.sgbdevapps.space360.data.network.NetworkConnectivityManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import javax.inject.Inject

@HiltViewModel
class IssueDetailViewModel @Inject constructor(
    private val issueRepository: IssueRepository,
    private val networkConnectivity: NetworkConnectivityManager
) : ViewModel() {
    
    // State
    private val _issue = MutableStateFlow<Issue?>(null)
    val issue: StateFlow<Issue?> = _issue.asStateFlow()
    
    private val _comments = MutableStateFlow<List<IssueComment>>(emptyList())
    val comments: StateFlow<List<IssueComment>> = _comments.asStateFlow()
    
    private val _photos = MutableStateFlow<List<IssuePhoto>>(emptyList())
    val photos: StateFlow<List<IssuePhoto>> = _photos.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _isOnline = MutableStateFlow(true)
    val isOnline: StateFlow<Boolean> = _isOnline.asStateFlow()
    
    private val _pendingSyncCount = MutableStateFlow(0)
    val pendingSyncCount: StateFlow<Int> = _pendingSyncCount.asStateFlow()
    
    // Last cache update timestamp (for "cached X hours ago" indicator)
    private val _lastCacheUpdateTime = MutableStateFlow<Long?>(null)
    val lastCacheUpdateTime: StateFlow<Long?> = _lastCacheUpdateTime.asStateFlow()
    
    init {
        // Observe connectivity
        viewModelScope.launch {
            networkConnectivity.isOnline.collect { online ->
                _isOnline.value = online
            }
        }
        
        // Observe pending sync count
        viewModelScope.launch {
            issueRepository.observePendingSyncCount().collect { count ->
                _pendingSyncCount.value = count
            }
        }
    }
    
    fun loadIssueDetail(issueId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = issueRepository.getIssueDetail(issueId)
                _issue.value = result.getOrNull()
                _lastCacheUpdateTime.value = System.currentTimeMillis()
                
                if (result.isFailure) {
                    _error.value = result.exceptionOrNull()?.message
                }
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun updateIssueStatus(issueId: String, newStatus: String) {
        viewModelScope.launch {
            try {
                val result = issueRepository.updateIssueStatus(
                    issueId = issueId,
                    newStatus = newStatus,
                    contractorId = "current_user_id" // TODO: Get from auth
                )
                
                if (result.isSuccess) {
                    // Optimistic update
                    _issue.value = _issue.value?.copy(status = newStatus)
                    _error.value = null
                } else {
                    _error.value = result.exceptionOrNull()?.message
                }
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
    
    fun addComment(issueId: String, text: String) {
        viewModelScope.launch {
            try {
                val result = issueRepository.addComment(
                    issueId = issueId,
                    text = text,
                    contractorId = "current_user_id"
                )
                
                if (result.isSuccess) {
                    // Add to comments immediately (optimistic)
                    val newComment = IssueComment(
                        id = "temp_${System.nanoTime()}",
                        issueId = issueId,
                        text = text,
                        authorId = "current_user_id",
                        createdAt = System.currentTimeMillis(),
                        status = "PENDING" // From Feature B
                    )
                    _comments.value = _comments.value + newComment
                    _error.value = null
                } else {
                    _error.value = result.exceptionOrNull()?.message
                }
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
    
    fun addPhotos(issueId: String, photoFilePaths: List<String>) {
        viewModelScope.launch {
            for (filePath in photoFilePaths) {
                try {
                    // Upload each photo
                    val result = issueRepository.addPhotoToIssue(
                        issueId = issueId,
                        filePath = filePath
                    )
                    
                    if (result.isSuccess) {
                        // Add to photos immediately (optimistic)
                        val newPhoto = IssuePhoto(
                            id = "temp_${System.nanoTime()}",
                            issueId = issueId,
                            photoUrl = filePath, // Local path until synced
                            uploadedAt = System.currentTimeMillis(),
                            status = "PENDING"
                        )
                        _photos.value = _photos.value + newPhoto
                    }
                } catch (e: Exception) {
                    _error.value = "Failed to upload photo: ${e.message}"
                }
            }
        }
    }
    
    fun retrySync(itemId: String? = null) {
        // Trigger SyncWorker.triggerImmediateSyncOnConnectivity()
        // This is handled by Feature B; just expose as method for UI
        viewModelScope.launch {
            // Call SyncWorker.triggerImmediateSyncOnConnectivity(context)
            // Implementation depends on how AG exposed it in Feature B
        }
    }
    
    fun clearError() {
        _error.value = null
    }
}
```

### IssuesListViewModel (Extend from Phase 1)

```kotlin
// Add to existing IssuesListViewModel:

// State for filters
private val _selectedStatusFilter = MutableStateFlow<String?>(null)
val selectedStatusFilter: StateFlow<String?> = _selectedStatusFilter.asStateFlow()

private val _selectedSiteFilter = MutableStateFlow<String?>(null)
val selectedSiteFilter: StateFlow<String?> = _selectedSiteFilter.asStateFlow()

private val _selectedPriorityFilter = MutableStateFlow<String?>(null)
val selectedPriorityFilter: StateFlow<String?> = _selectedPriorityFilter.asStateFlow()

private val _searchQuery = MutableStateFlow("")
val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

// Filtered issues (derived from issues + filters)
val filteredIssues: StateFlow<List<Issue>> = combine(
    issues,
    selectedStatusFilter,
    selectedSiteFilter,
    selectedPriorityFilter,
    searchQuery
) { allIssues, status, site, priority, query ->
    allIssues.filter { issue ->
        (status == null || issue.status == status) &&
        (site == null || issue.siteId == site) &&
        (priority == null || issue.priority == priority) &&
        (query.isEmpty() || issue.title.contains(query, ignoreCase = true) || 
         issue.description.contains(query, ignoreCase = true))
    }
}.stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

fun updateStatusFilter(status: String?) {
    _selectedStatusFilter.value = status
}

fun updateSiteFilter(site: String?) {
    _selectedSiteFilter.value = site
}

fun updatePriorityFilter(priority: String?) {
    _selectedPriorityFilter.value = priority
}

fun updateSearchQuery(query: String) {
    _searchQuery.value = query
}

fun refreshIssues() {
    // Force fresh network fetch (bypass cache TTL)
    viewModelScope.launch {
        loadIssues(forceRefresh = true)
    }
}
```

---

## API Integration

### Existing Endpoints (All Used in Feature A)

| Endpoint | Method | Purpose | Feature A Usage |
|---|---|---|---|
| `/api/issues?assigned_to=...&site_id=...` | GET | List contractor's issues | IssuesListScreen (initial load + refresh) |
| `/api/issues/{id}` | GET | Get issue detail | IssueDetailScreen (load detail + comments + photos) |
| `/api/issues/{id}` | PUT | Update issue | IssueDetailViewModel.updateIssueStatus() → queued via Feature B |
| `/api/issues/{id}/comments` | POST | Add comment | IssueDetailViewModel.addComment() → queued via Feature B |
| `/api/issues/{id}/photos` | POST | Upload photo | IssueDetailViewModel.addPhotos() → queued via Feature B |

### Request/Response Examples

```json
// GET /api/issues?assigned_to=contractor_123&site_id=site_456
{
  "issues": [
    {
      "id": "issue_001",
      "site_id": "site_456",
      "title": "Leak in bathroom",
      "description": "Water dripping from ceiling junction",
      "status": "Open",
      "priority": "High",
      "created_at": "2026-12-01T08:00:00Z",
      "updated_at": "2026-12-01T10:00:00Z",
      "assigned_to": "contractor_123",
      "photos": [
        {
          "id": "photo_001",
          "issue_id": "issue_001",
          "photo_url": "https://storage.googleapis.com/...",
          "uploaded_at": "2026-12-01T09:00:00Z"
        }
      ],
      "comments": [
        {
          "id": "comment_001",
          "issue_id": "issue_001",
          "text": "Investigating source",
          "author_id": "contractor_123",
          "created_at": "2026-12-01T09:30:00Z"
        }
      ]
    }
  ]
}

// PUT /api/issues/issue_001
{
  "status": "In Progress"
}

// POST /api/issues/issue_001/comments
{
  "text": "Fixed the leak"
}

// POST /api/issues/issue_001/photos
// Multipart form-data: file (binary), description (optional)
{
  "photo_id": "photo_123",
  "issue_id": "issue_001",
  "photo_url": "https://storage.googleapis.com/.../photo_123.jpg",
  "uploaded_at": "2026-12-01T11:00:00Z"
}
```

### Error Handling

```kotlin
// All errors are:
// 1. Shown to user as toasts (short-lived, dismissible)
// 2. Logged for debugging (Logcat)
// 3. For sync operations: shown as badges (red "Retry" via Feature B)

// Examples:
"Network error: Unable to connect" → Toast + retry available
"Invalid credentials" → Auto-logout (401 via Feature B)
"Photo too large (>5MB)" → Toast (client-side validation before upload)
"Upload failed" → Badge on photo + retry button
```

---

## Photo Upload & Display

### Photo Selection Flow

```
User taps "+ Add Photos"
    ↓
File picker opens (multi-select enabled)
    ↓
User selects 1+ JPG/PNG files (max 5MB each, validate client-side)
    ↓
Preview shown in gallery (local bitmap from file)
    ↓
Call IssueRepository.addPhotoToIssue() for each file
    ↓
Photo queued via Feature B's sync queue (if offline, queued locally)
    ↓
Show "pending" badge on thumbnail
    ↓
WorkManager syncs (Feature B): POST /api/issues/{id}/photos
    ↓
Backend returns signed GCS URL
    ↓
Update photo entity with URL, remove "pending" badge
    ↓
Display final GCS-hosted image
```

### Photo Display (Lightbox)

```kotlin
// Lightbox component:
@Composable
fun PhotoLightbox(
    photos: List<IssuePhoto>,
    initialIndex: Int = 0,
    onDismiss: () -> Unit
) {
    // Full-screen display
    // Swipe left/right to navigate
    // Pinch-to-zoom
    // Double-tap to zoom
    // Show photo count + upload metadata
    // ESC / back button to close
}

// Photo loading:
// Use Coil to load from GCS URL
// Cache locally (Coil handles this)
// If offline and photo not cached: show placeholder + "offline" indicator
```

### Upload Constraints

- **File types:** JPG, PNG only (validate before picker opens)
- **File size:** Max 5MB per file (validate after selection)
- **Multiple files:** Allow up to 10 photos per issue (soft limit)
- **Retry:** On upload failure, show retry button; retry up to 5 times (Feature B)

---

## Offline Behavior

### What Works Offline

✅ **Read:** View cached issues (list + detail + comments + photos)  
✅ **Optimistic writes:** Queue status updates, comments, photos locally  
✅ **Sync queue:** Operations persist in Room; synced on reconnect  

### What Doesn't Work Offline

❌ **Add new photos:** File picker can work, but upload is queued; GCS URLs unavailable until sync  
❌ **Refresh data:** Pull-to-refresh disabled (no network to fetch)  
❌ **Real-time updates:** No WebSocket; changes only sync every 15 min (Feature B)  

### Offline Indicators

- **Offline banner** (Feature B): Amber banner at top of IssuesListScreen
- **Cached indicator** (IssueDetailScreen): "Cached X hours ago" under title (if data stale)
- **Sync badges** (Feature B): Yellow "Syncing" / Red "Retry" on cards/items
- **Disabled inputs:** Comment input + photo upload disabled with hint "Offline — will sync when online"
- **Pull-to-refresh:** Disabled with hint "Offline — can't refresh"

---

## Testing Strategy

### Unit Tests

```kotlin
// IssueDetailViewModel
@Test
fun testLoadIssueDetail_setsIssueState() = runTest {
    // Mock repository
    // Call loadIssueDetail()
    // Assert issue state updated
}

@Test
fun testAddComment_queuesCommentLocally() = runTest {
    // Mock repository
    // Call addComment()
    // Assert comment added to _comments state immediately
    // Assert sync queue operation created (via Feature B mock)
}

@Test
fun testUpdateIssueStatus_queuesStatusUpdate() = runTest {
    // Call updateIssueStatus()
    // Assert issue.status updated immediately
    // Assert sync queue operation created
}

// IssuesListViewModel
@Test
fun testFilteredIssues_appliesStatusFilter() = runTest {
    // Set up issues with mixed statuses
    // Call updateStatusFilter("In Progress")
    // Assert filteredIssues contains only "In Progress" issues
}

@Test
fun testSearchQuery_findsIssuesByTitle() = runTest {
    // Set up issues with known titles
    // Call updateSearchQuery("leak")
    // Assert filteredIssues contains only matching issues
}
```

### Integration Tests

```kotlin
// Full workflow: Load → Detail → Update Status → Add Comment → Add Photo
@Test
fun testCompleteIssueWorkflow() = runTest {
    // 1. Load issues (from cache or network)
    // 2. Navigate to detail
    // 3. Verify detail loads (comments, photos)
    // 4. Update status (should queue)
    // 5. Add comment (should queue)
    // 6. Add photo (should queue)
    // 7. Verify all operations in sync queue
    // 8. Trigger sync (WorkManager)
    // 9. Verify all operations synced (marked SYNCED in queue)
}
```

### E2E Tests (Manual)

1. **List Screen:**
   - Launch app → issues load
   - Apply filter (status) → list updates
   - Search for issue → results show
   - Pull-to-refresh → fresh data fetches
   - Offline: pull-to-refresh disabled, cached data shown

2. **Detail Screen:**
   - Tap issue → detail opens
   - Comments visible + in chronological order
   - Photos visible in grid + lightbox works
   - Status update queues (optimistic)
   - Add comment queues (optimistic)
   - Add photos queues (optimistic)
   - Offline: inputs disabled with hint

3. **Sync Workflow:**
   - Go offline → make changes (status, comment, photo)
   - See "pending" badges
   - Reconnect → see "syncing" → badges clear
   - Verify backend received all changes

4. **Error Handling:**
   - Status update fails → see error toast + retry button
   - Comment add fails → see error badge + retry
   - Photo upload fails → see error badge + retry
   - Network timeout → graceful fallback to cache

---

## Success Criteria (Feature A Complete)

- ✅ Issues list loads (contractor's assigned issues only)
- ✅ Filters work (status, site, priority) + search by title/description
- ✅ Pull-to-refresh forces fresh network fetch
- ✅ Issue detail screen opens (title, description, metadata, comments, photos)
- ✅ Photo gallery displays all photos in responsive grid
- ✅ Can add photos (multi-select, JPG/PNG, preview, queue upload)
- ✅ Lightbox works (full-size, swipe nav, pinch-zoom)
- ✅ Can update status (Open → In Progress → Done, queued via Feature B)
- ✅ Can add comments (text input, queued, appear immediately with "pending" badge)
- ✅ Offline mode: read cached data, queue writes, disable inputs with hints
- ✅ Sync badges work (yellow "syncing" / red "retry" + update in real-time)
- ✅ Zero crashes on SDK 26+ devices
- ✅ No data leaks (contractor sees only assigned issues)
- ✅ Tests passing (unit + integration ≥70% coverage)
- ✅ Code review approved

---

## Dependencies

```gradle
// Already in Phase 1:
// - Jetpack Compose
// - Hilt
// - Retrofit + OkHttp
// - Room
// - Coroutines + Flow
// - Firebase Auth

// Feature A adds:
// - Coil (image loading) — should already be Phase 1; if not, add:
//   implementation("io.coil-kt:coil-compose:2.5.0")

// - PhotoPicker (Android 13+ native; fallback to file picker for older):
//   Can use Android's native intent ACTION_PICK
//   Or add library if needed: implementation("com.google.android.gms:play-services-files:18.0.1")
```

---

## Deliverables After AG

**Screens:**
- `com/sgbdevapps/space360/presentation/screens/IssuesListScreen.kt`
- `com/sgbdevapps/space360/presentation/screens/IssueDetailScreen.kt`
- `com/sgbdevapps/space360/presentation/screens/StatusUpdateBottomSheet.kt`

**Components:**
- `com/sgbdevapps/space360/presentation/components/IssueCard.kt`
- `com/sgbdevapps/space360/presentation/components/PhotoGallery.kt`
- `com/sgbdevapps/space360/presentation/components/PhotoLightbox.kt`
- `com/sgbdevapps/space360/presentation/components/CommentThread.kt`
- `com/sgbdevapps/space360/presentation/components/CommentInputField.kt`
- `com/sgbdevapps/space360/presentation/components/FilterPanel.kt` (inline filters)

**ViewModels:**
- `com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModel.kt`
- Updated `IssuesListViewModel.kt` (add filters + search)

**Repository Updates:**
- `com/sgbdevapps/space360/domain/repositories/IssueRepositoryImpl.kt`
  - Add `getIssueDetail(issueId)` method (offline-aware)
  - Add `addPhotoToIssue(issueId, filePath)` method (queue via Feature B)
  - Ensure `addComment()` + `updateIssueStatus()` queue via Feature B

**Tests:**
- `com/sgbdevapps/space360/presentation/viewmodels/IssueDetailViewModelTest.kt`
- `com/sgbdevapps/space360/presentation/viewmodels/IssuesListViewModelTest.kt`
- Updated repository tests

**Manifest Updates:**
- Add `READ_EXTERNAL_STORAGE` permission (photo picker)
- Add `WRITE_EXTERNAL_STORAGE` permission (if caching photos locally)
- Add `QUERY_ALL_PACKAGES` permission (if using third-party camera apps — likely not needed Phase 2)

---

## Notes for AG

1. **Offline-First:** Feature B is foundational. All reads should default to Room cache. Network fetches are "nice to have" but offline with stale cache is acceptable.

2. **Sync Queue:** Feature B's SyncQueueEntity handles all write operations. Feature A doesn't need to know about queueing; just call Repository methods and they queue automatically.

3. **Coil Caching:** Coil automatically caches images to disk. GCS signed URLs have 1-hour TTL; if photo displays after URL expires, Coil will fetch fresh (backend returns 403, show placeholder).

4. **Contractor-Scoped Data:** Backend enforces RBAC (contractors see only assigned issues). Don't add client-side filtering for this; trust backend.

5. **Error Handling:** Network errors should show as toasts (short-lived, dismissible). Sync failures show as badges (Feature B). No aggressive error dialogs.

6. **Pull-to-Refresh:** Disable offline; show hint "Offline — can't refresh" or just don't show loading indicator.

7. **LazyColumn Performance:** Test list rendering with 100+ issues. If jank, implement pagination or lazy loading.

8. **Photo Upload Flow:** Multi-select is key. Show previews immediately (local bitmaps). Queue for sync. Display GCS URL once synced. Handle failures gracefully (retry).

9. **Status Workflow Constraint:** Open → In Progress → Done (no reverse transitions, no skipping). Enforce UI-side (only show valid transitions). Backend also enforces.

10. **Comments Thread:** Show in chronological order (oldest first, newest at bottom). Pending comments show badge. On sync, remove badge.

---

## Success Metrics (When Complete)

- **Code Quality:** Clean architecture, MVVM pattern, 70%+ test coverage
- **Performance:** List renders 100+ issues smoothly; no ANR on detail screen
- **User Experience:** No unexpected crashes; errors clearly communicated; offline UX intuitive
- **Compliance:** Contractor-scoped (backend enforces); no data leaks; secure API calls (JWT tokens)

---

**Ready for AG. Send this prompt when Feature B is fully tested and approved. Expected delivery: 2–3 weeks.** 🚀
