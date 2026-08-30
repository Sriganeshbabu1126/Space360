package com.sgbdevapps.space360.data.repository

import android.util.Log
import com.sgbdevapps.space360.data.local.SiteDao
import com.sgbdevapps.space360.data.local.SiteEntity
import com.sgbdevapps.space360.data.remote.SitesService
import com.sgbdevapps.space360.domain.model.Site
import com.sgbdevapps.space360.domain.repository.SiteRepository
import javax.inject.Inject

class SiteRepositoryImpl @Inject constructor(
    private val sitesService: SitesService,
    private val siteDao: SiteDao
) : SiteRepository {

    override suspend fun getAssignedSites(): Result<List<Site>> {
        return try {
            val response = sitesService.getAssignedSites()
            val sites = response.map {
                Site(
                    id = it.id,
                    name = it.name,
                    location = it.location,
                    status = it.status,
                    openIssuesCount = it.open_issues_count
                )
            }

            // Cache locally
            siteDao.insertSites(sites.map { site ->
                SiteEntity(
                    id = site.id,
                    name = site.name,
                    location = site.location,
                    status = site.status,
                    openIssuesCount = site.openIssuesCount
                )
            })

            Result.success(sites)
        } catch (e: Exception) {
            Log.e("SiteRepository", "Get assigned sites failed: ${e.message}")
            // Fallback to local cache
            val cachedSites = siteDao.getAllSites().map {
                Site(
                    id = it.id,
                    name = it.name,
                    location = it.location,
                    status = it.status,
                    openIssuesCount = it.openIssuesCount
                )
            }
            if (cachedSites.isNotEmpty()) {
                Result.success(cachedSites)
            } else {
                Result.failure(e)
            }
        }
    }

    override suspend fun getSiteById(id: String): Result<Site> {
        return try {
            val response = sitesService.getSiteById(id)
            val site = Site(
                id = response.id,
                name = response.name,
                location = response.location,
                status = response.status,
                openIssuesCount = response.open_issues_count
            )
            Result.success(site)
        } catch (e: Exception) {
            Log.e("SiteRepository", "Get site by id failed: ${e.message}")
            Result.failure(e)
        }
    }
}
