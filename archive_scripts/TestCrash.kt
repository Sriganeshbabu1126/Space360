import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class TestCrash {
    init {
        println("Init block running")
        loadDashboard()
    }

    private val _userRole = MutableStateFlow<String>("Contractor")

    private fun loadDashboard() {
        // Run immediately on the current thread
        runBlocking {
            println("Loading dashboard")
            _userRole.value = "Manager"
        }
    }
}

fun main() {
    TestCrash()
}
