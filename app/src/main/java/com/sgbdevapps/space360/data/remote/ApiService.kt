package com.sgbdevapps.space360.data.remote

import retrofit2.http.*

interface AuthService {
    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse
}

interface SitesService {
    @GET("api/sites")
    suspend fun getAssignedSites(): List<SiteResponse>

    @GET("api/sites/{id}")
    suspend fun getSiteById(@Path("id") id: Int): SiteResponse
}

interface IssuesService {
    @GET("api/sites/{siteId}/issues")
    suspend fun getIssuesBySite(@Path("siteId") siteId: Int): List<IssueResponse>

    @GET("api/issues/{id}")
    suspend fun getIssueById(@Path("id") id: Int): IssueResponse

    @PUT("api/issues/{id}")
    suspend fun updateIssueStatus(
        @Path("id") id: Int,
        @Body request: UpdateIssueStatusRequest
    ): IssueResponse

    @POST("api/issues/{id}/comments")
    suspend fun addComment(
        @Path("id") issueId: Int,
        @Body request: AddCommentRequest
    ): IssueCommentResponse

    @Multipart
    @POST("api/issues/{id}/photos")
    suspend fun uploadPhoto(
        @Path("id") issueId: Int,
        @Part file: okhttp3.MultipartBody.Part
    ): IssuePhotoResponse
}
