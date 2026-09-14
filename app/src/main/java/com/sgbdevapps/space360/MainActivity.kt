package com.sgbdevapps.space360

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.sgbdevapps.space360.presentation.navigation.NavGraph
import com.sgbdevapps.space360.presentation.navigation.Route
import com.sgbdevapps.space360.presentation.viewmodels.AuthViewModel
import com.sgbdevapps.space360.presentation.viewmodels.MainViewModel
import android.widget.Toast
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.graphics.Color
import com.sgbdevapps.space360.presentation.viewmodels.SettingsViewModel
import com.sgbdevapps.space360.presentation.theme.Space360Theme
import dagger.hilt.android.AndroidEntryPoint
import com.sgbdevapps.space360.worker.SyncWorker
import javax.inject.Inject

import androidx.navigation.compose.currentBackStackEntryAsState

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject lateinit var authRepository: com.sgbdevapps.space360.domain.repository.AuthRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Phase 4: Offline Sync Periodic Worker
        SyncWorker.schedulePeriodicSync(this)
        
        setContent {
            Space360Theme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    MainApp()
                }
            }
        }
    }
}

@Composable
fun MainApp(
    viewModel: AuthViewModel = hiltViewModel(),
    settingsViewModel: SettingsViewModel = hiltViewModel(),
    mainViewModel: MainViewModel = hiltViewModel()
) {
    val navController = rememberNavController()
    val isLoggedIn by viewModel.isLoggedIn.collectAsState()
    val selectedColorScheme by settingsViewModel.colorScheme.collectAsState()
    
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    // Force recomposition when theme changes
    LaunchedEffect(selectedColorScheme) {
    }
    
    Space360Theme(colorScheme = selectedColorScheme) {
    Scaffold(
        bottomBar = {
            if (currentRoute != null && currentRoute != Route.Login.route) {
                val selectedSite by mainViewModel.selectedSite.collectAsState()
                BottomNavigationBar(navController, selectedSite != null)
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding).fillMaxSize()) {
            NavGraph(navController, isLoggedIn)
        }
    }
    }
}

@Composable
fun BottomNavigationBar(navController: NavHostController, isProjectSelected: Boolean) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route
    
    NavigationBar(modifier = Modifier.fillMaxWidth()) {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Home, contentDescription = "Dashboard") },
            label = { Text("Dashboard") },
            selected = currentRoute == Route.Dashboard.route,
            onClick = { navController.navigate(Route.Dashboard.route) }
        )
        val context = LocalContext.current
        NavigationBarItem(
            icon = { Icon(Icons.Default.List, contentDescription = "Issues", tint = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            label = { Text("Issues", color = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            selected = currentRoute?.startsWith("issues") == true,
            onClick = {
                if (isProjectSelected) {
                    navController.navigate(Route.IssuesList.route.replace("{siteId}", "all"))
                } else {
                    Toast.makeText(context, "Please select a project first", Toast.LENGTH_SHORT).show()
                }
            }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Add, contentDescription = "Capture", tint = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            label = { Text("Capture", color = if (isProjectSelected) MaterialTheme.colorScheme.onSurface else Color.Gray) },
            selected = currentRoute == Route.Capture.route,
            onClick = {
                if (isProjectSelected) {
                    navController.navigate(Route.Capture.route)
                } else {
                    Toast.makeText(context, "Please select a project first", Toast.LENGTH_SHORT).show()
                }
            }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
            label = { Text("Settings") },
            selected = currentRoute == Route.Settings.route,
            onClick = { navController.navigate(Route.Settings.route) }
        )
    }
}

@Composable
fun Box(modifier: Modifier, content: @Composable () -> Unit) {
    androidx.compose.foundation.layout.Box(modifier = modifier) {
        content()
    }
}
