# New Chat Setup — Migration Instructions

## Quick Start (3 steps)

### Step 1: Save the Summary
Save `CHAT_SUMMARY_2026-08-29.md` to:
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

[PASTE ENTIRE CHAT_SUMMARY_2026-08-29.md HERE]

You are acting as senior technical consultant and AG prompt architect.
- Do NOT write implementation code directly
- Draft precise AG prompts for me to send to AG (Antigravity IDE)
- Wait for my instruction before drafting any prompt

The immediate next step is to:
1. Fix the stitch status reporting bug (ffmpeg succeeds but job reports failed)
2. Verify the upload step end-to-end
3. Then proceed to Prompt #8 — MediaSDK C++ bridge
```

---

## What to Do First in the New Chat

**If verifying upload step:**
```
Let's first verify the upload step works end-to-end.
Guide me through a clean pipeline run and confirm GCS files appear.
```

**If fixing stitch reporting bug:**
```
Draft a debug prompt for AG to fix the stitch status reporting bug.
ffmpeg encodes successfully but the job sometimes reports stitch: failed.
The bug is likely in pipeline_runner.py result propagation.
```

**If ready for Prompt #8 (MediaSDK):**
```
Both upload and stitch are verified working.
Draft Prompt #8 — MediaSDK C++ bridge using Desktop-MediaSDK-Cpp at F:\Insta360_SDK\
```

---

## Key Things to Confirm in New Chat

Before Prompt #8 (MediaSDK bridge), confirm:

1. ✅ Is the production server GPU driver 610.00 or newer?
   (MediaSDK requires this — GTX 950M dev machine is too old)

2. ✅ Is the upload step verified end-to-end?
   (Server crashed during live test — needs re-verification)

3. ✅ Is the stitch status reporting bug fixed?
   (ffmpeg succeeds but job sometimes reports stitch: failed)

---

## Remaining Build Sequence

| Prompt | Task | Status |
|--------|------|--------|
| #4 | Metadata Extraction | ✅ Done |
| #5 | ffmpeg Stitching (adaptive codec) | ✅ Done |
| #6 | GCS Upload | ✅ Done |
| #7 | Space360 Integration Interface | ✅ Done |
| Fix | Stitch status reporting bug | ⚠️ Needed |
| Fix | Upload step verification | ⚠️ Needed |
| #8 | MediaSDK C++ Bridge | ⏸️ Not started |

---

## Critical Path Notes

- **ffmpeg absolute path**: `C:\ffmpeg\bin\ffmpeg.exe` (must NOT use PATH)
- **exiftool absolute path**: `F:\exiftool\exiftool.exe` (must NOT use PATH)
- **SDK location**: `F:\Insta360_SDK\Desktop-MediaSDK-Cpp\`
- **GCS bucket**: `space360-insta360-output` (asia-southeast1)
- **GCS project**: `space360-114433`
- **Hand-off report**: `F:\Space360\modules\insta360\docs\Video module handoff_report.md`
- **NVENC disabled**: GTX 950M driver too old — codec list is libx265/libx264 only

---

**You are ready to continue. Good luck with Prompt #8!** 🚀
