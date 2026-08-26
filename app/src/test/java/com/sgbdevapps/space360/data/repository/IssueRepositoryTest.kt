package com.sgbdevapps.space360.data.repository

import com.sgbdevapps.space360.data.local.IssueCommentDao
import com.sgbdevapps.space360.data.local.IssueDao
import com.sgbdevapps.space360.data.local.IssuePhotoDao
import com.sgbdevapps.space360.data.remote.IssuesService
import com.sgbdevapps.space360.data.remote.IssueResponse
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever

class IssueRepositoryTest {

    @Mock
    private lateinit var issuesService: IssuesService

    @Mock
    private lateinit var issueDao: IssueDao

    @Mock
    private lateinit var commentDao: IssueCommentDao

    @Mock
    private lateinit var photoDao: IssuePhotoDao

    private lateinit var repository: IssueRepositoryImpl

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        repository = IssueRepositoryImpl(issuesService, issueDao, commentDao, photoDao)
    }

    @Test
    fun testGetIssuesBySiteSuccess() = runTest {
        val mockResponse = listOf(
            IssueResponse(
                id = 1,
                title = "Test Issue",
                description = "Test Description",
                site_id = 1,
                status = "Open",
                priority = "High",
                type = "defect",
                assigned_to = 1,
                assigned_to_name = "John",
                created_at = "2026-08-26",
                updated_at = "2026-08-26"
            )
        )
        whenever(issuesService.getIssuesBySite(1)).thenReturn(mockResponse)

        val result = repository.getIssuesBySite(1)

        assert(result.isSuccess)
        assert(result.getOrNull()?.size == 1)
    }
}
