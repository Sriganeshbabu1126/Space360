# Dashboard Navigation & Structure Refactor

This refactoring will radically simplify the dashboard UI. Instead of users seeing 10+ disjointed tabs that all require selecting a project or floor plan, the app will use a nested, context-aware flow:
**Home (Project Select) → Project Dashboard → Floor Plan Select → Feature (Captures/Issues)**

## User Review Required
> [!IMPORTANT]
> The requested changes involve modifying routing, Contexts, and deleting redundant pages. This will temporarily break some views while we rewire them to use the new `FloorPlanContext`. Please review the routing changes carefully.

## Proposed Changes

### 1. App Routing & Core
#### [MODIFY] `F:\Space360\dashboard\src\App.tsx`
- Remove `/sites`, `/videos`, `/videos/upload` routes.
- Reroute `/` to `HomePage` (Project Selector).
- Create nested routing under `/project/:projectId` mapping to `ProjectDashboard`.

#### [MODIFY] `F:\Space360\dashboard\src\context\SiteContext.tsx`
- Add `selectedFloorPlan` and `setSelectedFloorPlan`.
- Wrap ProjectDashboard routes with this context.
- (Will add `tenantId` logic for multi-tenancy as requested).

### 2. Layout & Navigation
#### [MODIFY] `F:\Space360\dashboard\src\components\Layout.tsx`
- Remove the old `navItems` array that listed all global features.
- Update the sidebar to dynamically show features ONLY when inside a project.
- Top bar will show "Current Project" and "Current Floor Plan".

#### [NEW] `F:\Space360\dashboard\src\pages\ProjectDashboard.tsx`
- A wrapper component that fetches the project data.
- Houses the Sidebar and Outlet for nested routes.

#### [NEW] `F:\Space360\dashboard\src\components\FloorPlanSelector.tsx`
- A dropdown/sidebar widget to select a floor plan within the active project.

### 3. Feature Pages Refactoring
#### [DELETE] `F:\Space360\dashboard\src\pages\SitesPage.tsx`
- Obsolete. Home page takes over project selection.

#### [DELETE] `F:\Space360\dashboard\src\pages\VideosPage.tsx`
- Obsolete. Video management merges into Captures.

#### [MODIFY] `F:\Space360\dashboard\src\pages\HomePage.tsx`
- Stripped down to simply list Projects/Sites.
- Clicking a project routes the user to `/project/:projectId/captures`.

#### [MODIFY] `F:\Space360\dashboard\src\pages\CapturesPage.tsx`
- Removes independent project selection logic.
- Adds `FloorPlanSelector`.
- Merges "Upload Video" tab into this page.

#### [MODIFY] `F:\Space360\dashboard\src\pages\IssuesPage.tsx`
- Uses global project context.
- Filters issues by `selectedFloorPlan`.

#### [MODIFY] `F:\Space360\dashboard\src\pages\ProjectMembersPage.tsx`
- Updates to query multi-tenant users (`/api/companies/{companyId}/users`).
- Note: Requires backend endpoints which we will need to implement later.

## Verification Plan
### Manual Verification
1. Open the dashboard at `/`. Verify it shows the project selection screen.
2. Select a project. Verify it routes to `/project/{id}/captures`.
3. Verify the sidebar now shows context-aware links (Captures, Issues, Members).
4. Select a Floor Plan from the new dropdown. Verify Captures update to reflect only that floor plan.
5. Navigate to Issues. Verify it filters by the selected floor plan.
