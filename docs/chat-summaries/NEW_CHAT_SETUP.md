# Space360 v2 Chat Migration Guide

## Instructions for Starting the New Session

Follow these exact steps to instantly synchronize Claude's context for Space360 v2 development:

1. **Open a brand new Claude chat window.**
2. **Attach the Kickoff File:** Upload `F:\Space360\docs\chat-summaries\CHAT_SUMMARY_v2_KICKOFF.md`.
3. **Copy and Paste the exact message below.** 
4. *(Optional)* Fill out the answers to the bracketed Q1-Q5 questions if you have the data, or just leave them as "Unknown right now".

---

## 📋 EXACT MESSAGE TO PASTE:

```text
Hello! I am continuing the development of the Space360 project. We just completed the v1.1.0 production deployment of the Insta360 video stitching module to Google Cloud Run, successfully integrated with our FastAPI backend and React frontend.

Please read the attached `CHAT_SUMMARY_v2_KICKOFF.md` file. It contains the complete frozen architecture decisions, file locations, known limitations, and the v2 Roadmap. 

Here are the answers to the Open Questions from the end of the last session:
- Q1 (Pannellum equirectangular verification): [Answer here, e.g., Yes, it worked perfectly!]
- Q2 (Cold start time): [Answer here, e.g., About 12 seconds on the first load.]
- Q3 (Unexpected Cloud Logging errors): [Answer here, e.g., None seen so far.]
- Q4 (Queue bottleneck from max-instances=1): [Answer here, e.g., Not yet, traffic is low.]
- Q5 (Ready for Firestore migration?): [Answer here, e.g., Yes, let's start with Priority 1: Firestore migration.]

Please acknowledge that you have absorbed the context and architecture decisions. Then, act as my Principal AI Engineer and generate the first AG Prompt for Priority 1 on our v2 Roadmap so we can begin coding!
```

---

## What to Expect Next
Once you paste this, Claude will:
1. Confirm it understands the Linux container architecture, FFmpeg fallback system, and the HTTP-only module boundary.
2. Formulate a comprehensive **Phase 4 (v2)** architecture plan for migrating our in-memory/file-based job state to Google Cloud Firestore.
3. Provide the first set of exact step-by-step instructions (AG Prompts) for you to execute.

## Pro-Tips for the New Chat
- **Don't change frozen architecture** unless absolutely necessary (e.g., don't try to switch back to Windows containers). 
- Always reference the `CHAT_SUMMARY_v2_KICKOFF.md` if Claude forgets a file path.
