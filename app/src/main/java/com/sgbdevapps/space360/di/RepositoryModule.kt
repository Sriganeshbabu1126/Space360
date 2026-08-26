package com.sgbdevapps.space360.di

import com.sgbdevapps.space360.data.repository.AuthRepositoryImpl
import com.sgbdevapps.space360.data.repository.IssueRepositoryImpl
import com.sgbdevapps.space360.data.repository.SiteRepositoryImpl
import com.sgbdevapps.space360.domain.repository.AuthRepository
import com.sgbdevapps.space360.domain.repository.IssueRepository
import com.sgbdevapps.space360.domain.repository.SiteRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(impl: AuthRepositoryImpl): AuthRepository

    @Binds
    @Singleton
    abstract fun bindIssueRepository(impl: IssueRepositoryImpl): IssueRepository

    @Binds
    @Singleton
    abstract fun bindSiteRepository(impl: SiteRepositoryImpl): SiteRepository
}
