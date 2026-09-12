package com.sgbdevapps.space360.domain.model

data class User(
    val id: String,
    val email: String,
    val displayName: String? = null,
    val role: String = "Contractor" // Admin, Manager, Contractor
)
