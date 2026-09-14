package com.sgbdevapps.space360.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navDeepLink
import com.sgbdevapps.space360.presentation.screens.LoginScreen
import com.sgbdevapps.space360.presentation.screens.ChangePasswordScreen
import com.sgbdevapps.space360.presentation.screens.DashboardScreen
import com.sgbdevapps.space360.presentation.screens.IssuesScreen
import com.sgbdevapps.space360.presentation.screens.IssueDetailScreen
import com.sgbdevapps.space360.presentation.screens.CaptureScreen
import com.sgbdevapps.space360.presentation.screens.ProfileScreen
import com.sgbdevapps.space360.presentation.screens.SettingsScreen
import com.sgbdevapps.space360.presentation.screens.QRScannerScreen
import com.sgbdevapps.space360.presentation.screens.CreateIssueScreen

sealed class Route(val route: String) {
    object Login : Route("login")
    object Dashboard : Route("dashboard")
    object IssuesList : Route("issues/{siteId}")
    object IssueDetail : Route("issue/{issueId}")
    object Capture : Route("capture")
    object Profile : Route("profile")
    object Settings : Route("settings")
    object CreateIssue : Route("create_issue")
    object QRScanner : Route("qr_scanner")
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
            DashboardScreen(
                navController = navController,
                onLogout = {
                    navController.navigate(Route.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        composable(Route.IssuesList.route) { backStackEntry ->
            val siteId = backStackEntry.arguments?.getString("siteId") ?: ""
            IssuesScreen(
                navController = navController,
                siteId = siteId,
                onQRScanClick = {
                    navController.navigate(Route.QRScanner.route)
                }
            )
        }
        composable(
            route = Route.IssueDetail.route,
            deepLinks = listOf(navDeepLink { uriPattern = "space360://issue/{issueId}" })
        ) { backStackEntry ->
            val issueId = backStackEntry.arguments?.getString("issueId") ?: ""
            IssueDetailScreen(navController, issueId)
        }
        composable(Route.Capture.route) {
            CaptureScreen(navController)
        }
        composable(Route.Profile.route) {
            ProfileScreen(navController)
        }
        composable(Route.Settings.route) {
            SettingsScreen(
                onLogout = {
                    navController.navigate(Route.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        composable(Route.CreateIssue.route) {
            CreateIssueScreen(navController)
        }
        composable(Route.QRScanner.route) {
            QRScannerScreen(
                onQRScanned = { issueId ->
                    navController.navigate("issue/$issueId") {
                        popUpTo(Route.QRScanner.route) { inclusive = true }
                    }
                },
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }
        composable("change_password") {
            ChangePasswordScreen(
                onPasswordChanged = {
                    navController.navigate(Route.Dashboard.route) {
                        popUpTo(Route.Login.route) { inclusive = true }
                    }
                }
            )
        }
    }
}
