package com.sgbdevapps.space360.data.remote

import com.google.gson.annotations.SerializedName

// Auth
data class LoginRequest(
    val email: String,
    val password: String
)

data class AuthResponse(
    val idToken: String,
    val user: UserResponse
)

data class UserResponse(
    val id: Int,
    val email: String,
    val display_name: String? = null,
    val role: String = "Contractor"
)

// Sites
data class SiteResponse(
    val id: Int,
    val name: String,
    val location: String,
    val status: String = "Active",
    val open_issues_count: Int = 0
)

// Issues
data class IssueResponse(
    val id: Int,
    val title: String,
    val description: String,
    val site_id: Int,
    val status: String = "Open",
    val priority: String = "Medium",
    val type: String = "defect",
    val assigned_to: Int,
    val assigned_to_name: String,
    val created_at: String,
    val updated_at: String,
    val comments: List<IssueCommentResponse> = emptyList(),
    val photos: List<IssuePhotoResponse> = emptyList()
)

data class IssueCommentResponse(
    val id: Int,
    val issue_id: Int,
    val user_id: Int,
    val user_name: String,
    val text: String,
    val created_at: String
)

data class IssuePhotoResponse(
    val id: Int,
    val issue_id: Int,
    val photo_url: String,
    val uploaded_at: String
)

data class UpdateIssueStatusRequest(
    val status: String
)

data class AddCommentRequest(
    val text: String
)

data class ErrorResponse(
    val detail: String
)
