package com.sgbdevapps.space360.domain.repository

import com.sgbdevapps.space360.domain.model.Site

interface SiteRepository {
    suspend fun getAssignedSites(): Result<List<Site>>
    suspend fun getSiteById(id: String): Result<Site>
}
