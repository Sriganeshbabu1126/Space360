package com.sgbdevapps.space360.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.sgbdevapps.space360.presentation.screens.LoginScreen
import com.sgbdevapps.space360.presentation.screens.DashboardScreen
import com.sgbdevapps.space360.presentation.screens.IssuesListScreen
import com.sgbdevapps.space360.presentation.screens.IssueDetailScreen
import com.sgbdevapps.space360.presentation.screens.CaptureScreen
import com.sgbdevapps.space360.presentation.screens.ProfileScreen

sealed class Route(val route: String) {
    object Login : Route("login")
    object Dashboard : Route("dashboard")
    object IssuesList : Route("issues/{siteId}")
    object IssueDetail : Route("issue/{issueId}")
    object Capture : Route("capture")
    object Profile : Route("profile")
}

@Composable
fun NavGraph(
    navController: NavHostController,
    isLoggedIn: Boolean
) {
    NavHost(
        navController = navController,
        startDestination = if (isLoggedIn) Route.Dashboard.route else Route.Login.route
    ) {
        composable(Route.Login.route) {
            LoginScreen(navController)
        }
        composable(Route.Dashboard.route) {
            DashboardScreen(navController)
        }
        composable(Route.IssuesList.route) { backStackEntry ->
            val siteId = backStackEntry.arguments?.getString("siteId") ?: ""
            IssuesListScreen(navController, siteId)
        }
        composable(Route.IssueDetail.route) { backStackEntry ->
            val issueId = backStackEntry.arguments?.getString("issueId") ?: ""
            IssueDetailScreen(navController, issueId)
        }
        composable(Route.Capture.route) {
            CaptureScreen(navController)
        }
        composable(Route.Profile.route) {
            ProfileScreen(navController)
        }
    }
}
