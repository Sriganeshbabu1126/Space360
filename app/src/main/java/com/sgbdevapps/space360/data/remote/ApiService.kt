package com.sgbdevapps.space360.data.remote

import retrofit2.http.*

interface AuthService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse
}

interface SitesService {
    @GET("sites")
    suspend fun getAssignedSites(): List<SiteResponse>

    @GET("sites/{id}")
    suspend fun getSiteById(@Path("id") id: String): SiteResponse
}

interface IssuesService {
    @GET("issues")
    suspend fun getIssuesBySite(@Query("site_id") siteId: String? = null): List<IssueResponse>

    @GET("issues/{id}")
    suspend fun getIssueById(@Path("id") id: String): IssueResponse

    @PUT("issues/{id}")
    suspend fun updateIssueStatus(
        @Path("id") id: String,
        @Body request: UpdateIssueStatusRequest
    ): IssueResponse

    @POST("issues/{id}/comments")
    suspend fun addComment(
        @Path("id") issueId: String,
        @Body request: AddCommentRequest
    ): IssueCommentResponse

    @Multipart
    @POST("issues/{id}/photos")
    suspend fun uploadPhoto(
        @Path("id") issueId: String,
        @Part file: okhttp3.MultipartBody.Part
    ): IssuePhotoResponse

    @POST("api/paths/")
    suspend fun createPath(
        @Body request: CreatePathRequest
    ): okhttp3.ResponseBody
}
