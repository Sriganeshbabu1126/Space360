package com.sgbdevapps.space360.presentation.screens

sealed class FloorPlanLoadState {
    object Loading : FloorPlanLoadState()
    object NoProject : FloorPlanLoadState()
    object NoFloorPlan : FloorPlanLoadState()
    data class Loaded(val url: String) : FloorPlanLoadState()
    data class Error(val message: String) : FloorPlanLoadState()
}
