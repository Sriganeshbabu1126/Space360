# Space360 Chat Summary — August 29, 2026
## Migration Handoff — Claude to Claude (New Chat)

---

## Project Context

Continuing development of **Space360**, a 360° field inspection platform for construction/site management. This session covered: Stage 2 completion confirmation, Stage 3 mobile strategy pivot (React Native → native apps), Insta360 X4 module planning, Android + iOS new chat setup, and master roadmap creation.

---

## Key Decisions Made This Session

| Decision | Choice | Reason |
|---|---|---|
| Stage 2 status | ✅ 100% Complete | #80 Data Export confirmed delivered by AG |
| #81 React Native | ❌ Cancelled | Replaced by native Android + iOS modules |
| Mobile strategy | Two separate native codebases | Hardware API access, Insta360 SDK, independent pipelines |
| Android framework | Kotlin + Jetpack Compose | Native Android, full hardware access |
| iOS framework | Swift — stack TBD in planning | Let iOS Claude recommend during planning session |
| Android min SDK | SDK 26 (Android 8.0) | Field device coverage + Compose/CameraX compatibility |
| iOS min version | iOS 16 | SwiftUI Navigation Stack, AVFoundation, SwiftData |
| Phase 1 scope (both) | Auth + Dashboard + Issue Viewer only | Tight scope, ship working, build on top |
| Primary user role (both) | Contractor-first | Field workers need mobile most urgently |
| Offline support (both) | Phase 2 — not Phase 1 | Architecture ready, sync queue deferred |
| UI/UX sync (Android/iOS) | Iterate independently | Follow platform native conventions (Material / HIG) |
| Insta360 module | Standalone — separate chat | Isolates complexity, parallel development |
| Video capture (iOS P2) | Image-only Phase 1, 360° video Phase 2 | Clean phase separation |
| Master roadmap format | .md + PDF, both generated | AI handoff reference + manager copy |
| Roadmap location | F:\Space360\docs\ | Centralised, uploaded to new chats as needed |
| Roadmap version | v1.0 (Aug 21, 2026) | First version — update on major milestones |

---

## Current Status

### ✅ Completed This Session
- Confirmed Stage 2 = 100% complete (#76 #77 #78 #79 #79.1 #80 all done)
- Cancelled #81 (React Native Mobile App Foundation)
- Created `SPACE360_MASTER_ROADMAP_v1.0.md` + `.pdf` — saved to `F:\Space360\docs\`
- Drafted + delivered Android module new chat prompt (planning session initiated)
- Answered Android planning questions (auth, roles, min SDK, offline, Phase 1 scope)
- Drafted + delivered iOS module new chat prompt (planning session initiated)
- Answered iOS planning questions (min iOS, Insta360 P2, offline, UI/UX sync)
- Drafted Insta360 X4 module new chat prompt

### 🔄 In Progress (Active in Separate Chats)
- **Android native module** — `F:\Space360\modules\android\` — planning session underway in separate Claude chat
- **iOS native module** — `F:\Space360\modules\ios\` — planning session underway in separate Claude chat
- **Insta360 X4 module** — `F:\Space360\modules\insta360\` — new Claude chat prompt ready, not yet started

### ⏸️ On Hold
- **Video capture (#84)** — blocked on 8 unanswered spec questions (see roadmap Section 9.5)
- **Path Tracking (#82)** — ready to proceed, not yet started
- **Path Navigation (#83)** — depends on #82

---

## Active Module Chats (Separate Windows)

| Module | Chat Status | Location | Notes |
|---|---|---|---|
| Android Native | 🔄 Planning underway | `F:\Space360\modules\android\` | Kotlin + Jetpack Compose confirmed |
| iOS Native | 🔄 Planning underway | `F:\Space360\modules\ios\` | Stack recommendation pending from Claude |
| Insta360 X4 | 🎯 Prompt ready, not started | `F:\Space360\modules\insta360\` | Python + FFmpeg + OpenCV |

---

## Next Steps (Priority Order)

1. **Android chat** — Wait for planning agenda from Claude, review, then request first AG prompt (Auth + Dashboard + Issue Viewer)
2. **iOS chat** — Wait for stack recommendation + planning agenda, review, then request first AG prompt
3. **Insta360 chat** — Open new Claude chat, paste the Insta360 prompt, begin planning
4. **Master Roadmap update** — After Android + iOS planning sessions finalise, update roadmap to v1.1 with confirmed tech stacks and module decisions
5. **Path Tracking (#82)** — Can start anytime independently; raise when ready

---

## Open Questions

| Question | Status |
|---|---|
| iOS tech stack recommendation | Pending — iOS Claude will propose in planning session |
| iOS AG prompt scope (Phase 1) | Pending — to be confirmed after planning |
| Android AG prompt scope (Phase 1) | Pending — to be confirmed after planning |
| 8 video spec questions (Insta360 X4 / video capture) | Still unanswered — not blocking current work |
| Insta360 module: FastAPI vs CLI interface | TBD in Insta360 planning chat |

---

## Tech Stack Summary

### Web App (Complete)
- Python 3.13 + FastAPI + PostgreSQL 16 + SQLAlchemy + Alembic
- React 18 + TypeScript + Tailwind v3.4.1 + React Router v7
- Firebase Auth · GCS bucket: `360-field-check-media-sgb` · Cloud Run
- Firebase project: `field-check-72967` · GCP region: `asia-southeast1`

### Android Module (Planning)
- Kotlin + Jetpack Compose + MVVM + Clean Architecture
- Hilt (DI) · Retrofit + OkHttp · Firebase Auth SDK
- DataStore · Coil · Coroutines + Flow · Min SDK 26

### iOS Module (Planning)
- Swift (latest stable) · UI framework TBD · Min iOS 16
- Stack recommendation pending from iOS Claude

### Insta360 Module (Planning)
- Python · FFmpeg + OpenCV · FastAPI or CLI (TBD)
- GCS SDK · Local Windows initially → Cloud Run later

---

## File & Folder Reference

| Item | Path |
|---|---|
| Project root | `F:\Space360\` |
| Backend | `F:\Space360\backend\` |
| Frontend | `F:\Space360\frontend\` |
| Android module | `F:\Space360\modules\android\` |
| iOS module | `F:\Space360\modules\ios\` |
| Insta360 module | `F:\Space360\modules\insta360\` |
| Docs / Roadmap | `F:\Space360\docs\` |
| Master Roadmap | `F:\Space360\docs\SPACE360_MASTER_ROADMAP_v1.0.md` |
| GitHub | https://github.com/Sriganeshbabu1126/Space360 |

---

## Known Gotchas

1. AG can lose context in long sessions — send explicit state reset if it drifts
2. Celery + Redis must be running locally for large export dev (#80)
3. Stage 1 must remain 100% backward compatible — permanent constraint
4. `google-services.json` (Android) + `GoogleService-Info.plist` (iOS) must be placed manually for Firebase — pending module setup
5. Master roadmap must be **uploaded** to each new chat — it is not auto-accessible from `F:\Space360\docs\`

---

## How to Use This Summary

Paste this file at the start of your new Claude chat along with the master roadmap (`SPACE360_MASTER_ROADMAP_v1.0.md`), then say:

> "I'm continuing Space360 development. Read the attached summary and roadmap, confirm your role as consultant/prompt architect, and wait for my first instruction."

---

*Generated: August 29, 2026*
*Session: Space360 Stage 2 completion + Stage 3 mobile strategy + module planning*
*Next chat focus: Android + iOS planning review, Insta360 chat initiation*
