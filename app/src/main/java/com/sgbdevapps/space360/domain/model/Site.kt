package com.sgbdevapps.space360.domain.model

data class Site(
    val id: Int,
    val name: String,
    val location: String,
    val status: String = "Active", // Active, Completed, On Hold
    val openIssuesCount: Int = 0
)
