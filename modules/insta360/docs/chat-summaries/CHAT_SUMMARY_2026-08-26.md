# New Chat Setup — Migration Instructions

## Quick Start (3 steps)

### Step 1: Download the Summary
Save `CHAT_SUMMARY_2026-08-26.md` to:
```
F:\Space360\modules\insta360\docs\chat-summaries\
```
And commit it to git as your decision log.

### Step 2: Start a New Chat
Open a fresh Claude chat session.

### Step 3: Paste & Prime the Context
Start the new chat with exactly this:

---

```
I am continuing development of the Insta360 X4 Video Handling Module —
a standalone sub-module of the Space360 project.

Here is the full context from my previous session:

[PASTE ENTIRE CHAT_SUMMARY_2026-08-26.md HERE]

You are acting as senior technical consultant and AG prompt architect.
- Do NOT write implementation code directly
- Draft precise AG prompts for me to send to AG (Antigravity IDE)
- Wait for my instruction before drafting any prompt

The immediate next step is to review the output of Prompt #4
(metadata extraction). I will share AG's result first.
```

---

## What to Do First in the New Chat

**If Prompt #4 is complete:**
Share AG's output and the sidecar JSON sample, then ask:
```
Review Prompt #4 output and draft Prompt #5 — MediaSDK C++ bridge and .insv stitching.
Before drafting, remind me to confirm my GPU availability.
```

**If Prompt #4 is still running:**
```
Prompt #4 is still in progress. Stand by — I will share AG's output shortly.
```

---

## Key Things to Confirm in New Chat

Before Prompt #5 (stitching), the new Claude instance must ask you to confirm:

1. ✅ Does your Windows machine have a **discrete GPU**?
   (MediaSDK 3.x.x requires this — integrated graphics will not work)

2. ✅ Which GPU? (NVIDIA preferred — MediaSDK uses CUDA/NPP libraries)

3. ✅ Is Visual Studio Build Tools installed?
   (Required to compile or link C++ SDK on Windows)

---

## Remaining Build Sequence

| Prompt | Task | Status |
|--------|------|--------|
| #4 | Metadata Extraction (exiftool + SDK stub) | 🔄 In Progress |
| #5 | MediaSDK C++ Bridge + .insv → MP4 Stitching | ⏸️ Not started |
| #6 | GCS Upload (stitched MP4 + sidecar JSON) | ⏸️ Not started |
| #7 | Space360 Integration Interface | ⏸️ Not started |

---

## Pro Tips

- Always share AG's full output before asking for the next prompt
- Run the live hardware test after every prompt (X4 + curl POST /ingest)
- Save sidecar JSONs from each test run — they show metadata quality improving
- Commit `transfer_manifest.json` examples to docs/ as reference samples

---

**You are ready to continue. Good luck with Prompt #5!** 🚀
