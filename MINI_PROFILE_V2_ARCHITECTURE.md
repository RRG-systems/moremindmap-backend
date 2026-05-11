# PREMIUM MINI PROFILE V2 — INTEGRATION ARCHITECTURE MAP

**Status:** PLANNING ONLY (No coding yet)  
**Date:** 2026-05-04 09:55 MST  
**Goal:** Parallel V2 flow alongside production V1

---

## CURRENT PRODUCTION (V1) — UNTOUCHED

```
POST /api/moremindmap/mini-profile
    ↓
server.js:177 (app.post)
    ↓
scoreAssessment("set_1", responses)  [/engine/scoreAssessment.js]
    ↓
generateMiniProfile(scoring)  [/engine/miniProfileGenerator.js]
    ↓
Return: { success, scoringPayload, miniProfile: { 16 JSON fields } }
    ↓
Frontend renders JSON (TBD frontend logic)
```

**Output:** JSON object, ~1,172 words  
**Pages:** N/A  
**Lifecycle:** Real-time response  

---

## PROPOSED V2 PREMIUM (PARALLEL)

```
POST /api/moremindmap/mini-profile-v2
    ↓
server.js:NEW (new app.post route)
    ↓
scoreAssessment("set_1", responses)  [REUSE from V1]
    ↓
NEW: generatePremiumMiniProfileV2(scoring)  [NEW backend file]
        ├─ Call GPT-5.5 for dense narratives
        ├─ Apply doctrine filter
        ├─ Generate signature codes
        ├─ Prepare renderer payload
        └─ Return narrative object
    ↓
NEW: generateMiniReportHTML(narratives, codes)  [NEW or use htmlRendererV5-PassA-Fixed.js]
    ↓
Decision fork (see below):
    ├─ Return JSON + download link?
    ├─ Stream PDF?
    ├─ Return HTML + instructions?
    └─ Generate async + return URL?
```

---

## ARCHITECTURE COMPONENT MAP

### LAYER 1: INPUT (Unchanged)

| Component | File | Status | Role |
|-----------|------|--------|------|
| Frontend form | `src/*` | REUSE | Submits 24 answers |
| Form submission | HTTP POST | REUSE | `/api/moremindmap/mini-profile-v2` |
| Request body | JSON | REUSE | Same 24-answer structure as V1 |

---

### LAYER 2: SCORING (Reused from V1)

| Component | File | Status | Role |
|-----------|------|--------|------|
| Scoring function | `engine/scoreAssessment.js` | **REUSE** | Convert answers → 8 dimensions |
| Output | Object | REUSE | `{ ranked, primary, secondary, normalized }` |

**No changes needed.** V2 will use identical scoring.

---

### LAYER 3: NEW — DENSE NARRATIVE GENERATION (V2-Specific)

#### 3A: GPT-5.5 Narrative Call

| Component | File | Status | Role |
|-----------|------|--------|------|
| **Entry point** | `engine/generatePremiumMiniProfileV2.js` | **NEW** | Orchestrates V2 generation |
| **GPT call** | `engine/generatePremiumMiniProfileV2.js` | **NEW** | Calls OpenAI GPT-5.5 with scoring payload |
| **Prompt engineering** | `engine/generatePremiumMiniProfileV2.js` | **NEW** | System prompts for dense behavioral intelligence |
| **Model** | OpenAI API | **REUSE** | Same as current system uses |
| **Token budget** | TBD | **NEW** | Estimate: ~4K tokens input + ~6K output per report |
| **Rate limiting** | TBD | **NEW** | May need async queue for production |

**New file needed:** `/backend/engine/generatePremiumMiniProfileV2.js`

```
Input: scoring object { ranked: [], normalized: {} }
Process:
  1. Extract primary/secondary/suppressed patterns
  2. Build prompt: "Generate dense behavioral intelligence for these patterns..."
  3. Call OpenAI with scoring context
  4. Parse response into narrative sections
Output: narrative object { executiveSummary, operatingPattern, ... }
```

---

#### 3B: Doctrine Filter Application

| Component | File | Status | Role |
|-----------|------|--------|------|
| **Doctrine filter** | `engine/mindMapDoctrineFilter.js` | **NEED TO LOCATE** | Cleans prose, removes raw decimals |
| **Input** | Raw narratives from GPT | **NEW** | Apply to narrative object |
| **Output** | Clean narratives | **NEW** | Doctrine-filtered prose ready for rendering |
| **Integration point** | After GPT call, before rendering | **NEW** | Pipeline: GPT → Filter → Renderer |

**Action needed:** Locate `mindMapDoctrineFilter.js` or create it if missing.

---

#### 3C: Signature Code Generation

| Component | File | Status | Role |
|-----------|------|--------|------|
| **Code generator** | `engine/signatureCodeGenerator.js` | **NEED TO CREATE** | Convert scores to V8, Fd4, F4, etc. |
| **Input** | Normalized scores `{ vector: 35.9, ... }` | **NEW** | Score object from scoreAssessment |
| **Output** | Code object `{ V: 8, Fd: 4, F: 4, ... }` | **NEW** | Signature codes for cover page |
| **Insertion** | generatePremiumMiniProfileV2.js | **NEW** | Call after scoring, before rendering |

**Action needed:** Create signature code conversion logic.

---

### LAYER 4: PAGE 2 SYSTEM MAP DATA (V2-Specific)

| Component | File | Status | Role |
|-----------|------|--------|------|
| **Map builder** | `engine/behavioralSystemMapBuilder.js` | **NEED TO CREATE** | Build 5-circle system data |
| **Input** | Scored patterns (primary/secondary/opposing) | **NEW** | Pattern structure from scoring |
| **Output** | JSON structure for renderer | **NEW** | `{ circles: [top, left, center, right, bottom], tensions: [...] }` |
| **Insertion** | generatePremiumMiniProfileV2.js | **NEW** | Call to build map data object |

**Action needed:** Create map builder logic (can be simple JSON structure, not visualization).

---

### LAYER 5: HTML RENDERING (V2-Specific)

| Component | File | Status | Role |
|-----------|------|--------|------|
| **Renderer** | `utils/htmlRendererV5-PassA-Fixed.js` | **REUSE** | Generate HTML from narratives |
| **Location** | Currently in moremindmap (not backend) | **MOVE/LINK** | Import into backend for server-side rendering |
| **Input** | Complete payload (narratives, scores, codes, map) | **NEW** | Full context for HTML generation |
| **Output** | HTML string (18 pages) | **NEW** | Ready for return or file generation |
| **Usage** | `generatePremiumMiniProfileV2.js` | **NEW** | Call renderer after all pipeline steps |

**Action needed:** Move or link htmlRendererV5-PassA-Fixed.js into backend, make it importable.

---

### LAYER 6: OUTPUT DECISION (Critical Architecture Choice)

#### **Option A: Return HTML + Auto-Download**

```
Response format: { success, html, filename, size }
Frontend: Display "Download Report" button
Lifecycle: Real-time (10-15 sec per report due to GPT call)
```

**Pros:** Instant delivery, browser handles download  
**Cons:** Large response payload, frontend must handle display/download

---

#### **Option B: Generate Async + Return URL**

```
Step 1: Accept request, queue job
Step 2: Return { success, jobId, statusUrl }
Step 3: Frontend polls /api/mini-profile-v2/status/:jobId
Step 4: When complete, return download URL
Step 5: Frontend offers download link
Lifecycle: Async, 5-30 seconds depending on queue
```

**Pros:** Non-blocking, can handle many requests, return immediately  
**Cons:** More complex architecture, needs job queue (Redis/Bull)

---

#### **Option C: Return JSON + HTML Both**

```
Response format: { success, miniProfile (JSON), htmlReport, codes }
Lifecycle: Real-time but slower due to both generations
```

**Pros:** Frontend has choice of rendering  
**Cons:** Larger payload, duplicate work

---

#### **RECOMMENDED FOR V2:** Option B (Async + URL)

**Rationale:**
- Production-ready for multiple concurrent users
- GPT-5.5 calls are slow (10-15 sec)
- Users expect real-time response, not hanging
- Can show progress to frontend ("Report generating...")
- Scales better for moremindmap.com traffic

---

### LAYER 7: ASYNC JOB QUEUE (If Option B chosen)

| Component | File | Status | Role |
|-----------|------|--------|------|
| **Queue system** | Bull/Redis (external) | **NEW** | Manage background jobs |
| **Job handler** | `jobs/generateMiniReportV2.js` | **NEW** | Background worker process |
| **Job processor** | node.js worker thread | **NEW** | Runs generatePremiumMiniProfileV2 |
| **Storage** | Redis or temp file storage | **NEW** | Store generated PDFs temporarily |
| **Cleanup** | Scheduler | **NEW** | Delete old reports (24h TTL) |

---

### LAYER 8: NEW BACKEND FILES REQUIRED

| File | Purpose | Lines Est. | Complexity |
|------|---------|-----------|------------|
| `engine/generatePremiumMiniProfileV2.js` | Main V2 orchestrator | 200-300 | High |
| `engine/signatureCodeGenerator.js` | Code conversion | 50-100 | Low |
| `engine/behavioralSystemMapBuilder.js` | Page 2 map data | 100-150 | Medium |
| `jobs/generateMiniReportV2.js` | Async job handler | 150-200 | High |
| `api/miniProfileV2Routes.js` | Separate route file | 80-120 | Medium |
| `lib/htmlReportGenerator.js` | Wrapper for renderer | 50-80 | Low |

**Total new backend code:** ~800-1,000 lines

---

### LAYER 9: MODIFIED BACKEND FILES

| File | Change | Impact | Notes |
|------|--------|--------|-------|
| `server.js` | Add V2 route handler | 10-20 lines | Point to separate route file |
| `package.json` | Add Bull/Redis if async | Minimal | Already has OpenAI |
| `.env` | Add V2 config vars | Minimal | Job queue, rate limits, etc. |

---

### LAYER 10: FRONTEND CHANGES (Estimate)

| Change | File | Impact | Required? |
|--------|------|--------|-----------|
| Add V2 form endpoint | `src/components/MiniProfileForm.jsx` | 5 lines | **YES** |
| Handle async response | `src/services/api.js` | 15 lines | **YES** |
| Show progress UI | `src/components/ReportProgress.jsx` | 100 lines | Optional but recommended |
| Handle download | `src/utils/download.js` | 20 lines | **YES** |
| Store job ID in state | `src/hooks/useMiniProfileV2.js` | 50 lines | **YES** |

**Frontend impact:** Minimal, mostly UI additions

---

## COMPLETE V2 DATA FLOW MAP

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: User submits 24-question form                         │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    POST /api/moremindmap/mini-profile-v2
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ BACKEND: server.js (NEW ROUTE)                                  │
│ app.post("/api/moremindmap/mini-profile-v2", ...)              │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                      Parse 24 answers from request
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ LAYER 1: SCORING (Reused from V1)                              │
│ scoreAssessment("set_1", responses)                            │
│ Output: { ranked, normalized, primary, secondary, ... }        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    Queue V2 job (Option B: Async)
                    Return: { jobId, statusUrl }
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ BACKGROUND WORKER: generateMiniReportV2Job                      │
│ (Runs in: Bull Queue / Node Worker Thread)                      │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ LAYER 2: GPT-5.5 DENSE NARRATIVE CALL                           │
│ generatePremiumMiniProfileV2(scoring)                           │
│ → Call OpenAI with prompt + context                             │
│ Output: { executiveSummary, operatingPattern, ... (12 sections)}│
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ LAYER 3: DOCTRINE FILTER                                        │
│ mindMapDoctrineFilter.js                                        │
│ Remove raw decimals, clean phrasing, validate quality          │
│ Output: Clean narrative object                                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ LAYER 4: SIGNATURE CODES                                        │
│ signatureCodeGenerator.js                                       │
│ Convert 35.9 → V8, 17.9 → Fd4, etc.                            │
│ Output: { V: 8, Fd: 4, F: 4, ... }                             │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ LAYER 5: PAGE 2 SYSTEM MAP DATA                                 │
│ behavioralSystemMapBuilder.js                                   │
│ Build 5-circle system structure                                 │
│ Output: { circles, tensions, labels }                           │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ LAYER 6: HTML RENDERING                                         │
│ htmlRendererV5-PassA-Fixed.js                                   │
│ Generate 18-page HTML from all components                       │
│ Output: HTML string (45KB+)                                     │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ LAYER 7: FILE GENERATION & STORAGE                              │
│ Save HTML to temp storage                                       │
│ Generate PDF (if needed)                                        │
│ Create download link                                            │
│ Output: { filename, url, filesize }                             │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    Job Complete: Store result
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│ FRONTEND: Poll /api/mini-profile-v2/status/:jobId               │
│ Receive: { status: "complete", downloadUrl, ... }              │
│ Display: "Your report is ready → Download"                     │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
              User clicks "Download" or views in browser
```

---

## GENERATION TIME ESTIMATES

| Step | Time | Bottleneck? |
|------|------|------------|
| Parse request | 10ms | No |
| Score assessment | 50ms | No |
| GPT-5.5 call | 8-15 sec | **YES** |
| Doctrine filter | 100ms | No |
| Signature codes | 10ms | No |
| Map builder | 20ms | No |
| HTML rendering | 100-200ms | No |
| File storage | 50ms | No |
| **TOTAL** | **8-15 sec** | GPT API latency |

**Production implication:** Async (Option B) essential to avoid user-facing timeout.

---

## ARCHITECTURE DIAGRAM (Text)

```
V1 PRODUCTION (Untouched)           V2 PREMIUM (New Parallel)
═══════════════════════════════════════════════════════════════

POST /mini-profile          →        POST /mini-profile-v2
        ↓                                    ↓
   scoreAssess                         scoreAssess (REUSE)
        ↓                                    ↓
generateMiniProfile              [Queue async job]
(thin JSON)                              ↓
        ↓                       [Background worker]
Return JSON                              ↓
(1,172 words, 16 fields)         GPT-5.5 call (8-15 sec)
        ↓                                  ↓
Frontend renders                   Doctrine filter
        ↓                                  ↓
User sees basic profile          Signature codes
                                         ↓
                               Map data builder
                                         ↓
                               HTML rendering
                                         ↓
                               Save to storage
                                         ↓
                           Return download URL
                                         ↓
                             User downloads/views
                            (18 pages, 3,912 words)

LIVE TRAFFIC: V1               TESTING: V2 (Parallel)
Users unaffected               Premium users opt-in
```

---

## SAFETY CONSIDERATIONS (Production)

| Risk | Mitigation |
|------|-----------|
| **GPT API rate limits** | Implement queue with backoff strategy |
| **Long generation time** | Async + progress UI, 60-sec timeout |
| **Storage bloat** | 24-hour TTL on generated files, auto-cleanup |
| **Concurrent requests** | Job queue handles 10-50 concurrent |
| **API key exposure** | Keep in .env, not in code |
| **User confusion** | Clear V1 vs V2 labeling in frontend |
| **Fallback if GPT fails** | Return V1 JSON fallback (graceful degrade) |

---

## DEPLOYMENT STRATEGY

### Phase 1: Internal Testing
- Deploy V2 on dev branch
- Test with team submissions
- Validate GPT output quality
- Profile generation time
- Check PDF/HTML rendering

### Phase 2: Beta Testing
- Deploy V2 behind feature flag
- Offer "Premium Report" option to select users
- Collect feedback on prose quality
- Monitor API costs
- Refine doctrine filter if needed

### Phase 3: Production Rollout
- Remove feature flag (all users access V2)
- Monitor performance
- Keep V1 as fallback option
- Track usage metrics

### Phase 4: V1 Deprecation (Future)
- Once V2 stable, deprecate V1
- Migrate historical users to V2
- Archive V1 code

---

## NEXT STEPS (After Architecture Approved)

1. ✅ **Architecture review** (this document)
2. ⏳ **Create backend file structure** (code)
3. ⏳ **Implement GPT prompt engineering** (code)
4. ⏳ **Wire doctrine filter** (code)
5. ⏳ **Implement signature codes** (code)
6. ⏳ **Add async job queue** (code)
7. ⏳ **Frontend integration** (code)
8. ⏳ **End-to-end testing** (QA)
9. ⏳ **Deployment** (DevOps)

---

## FILES REFERENCE

### Existing Files Used
- `/moremindmap-backend/server.js` — Modify (add V2 route)
- `/moremindmap-backend/engine/scoreAssessment.js` — Reuse (no change)
- `/moremindmap/utils/htmlRendererV5-PassA-Fixed.js` — Port to backend

### New Files to Create
- `/moremindmap-backend/engine/generatePremiumMiniProfileV2.js` — Main orchestrator
- `/moremindmap-backend/engine/signatureCodeGenerator.js` — Code conversion
- `/moremindmap-backend/engine/behavioralSystemMapBuilder.js` — Map builder
- `/moremindmap-backend/jobs/generateMiniReportV2.js` — Async job handler
- `/moremindmap-backend/api/miniProfileV2Routes.js` — V2 route definitions

### Frontend Files to Modify
- `/moremindmap/src/components/MiniProfileForm.jsx` — Add V2 endpoint
- `/moremindmap/src/services/api.js` — V2 API call
- `/moremindmap/src/hooks/useMiniProfileV2.js` — State management
- `/moremindmap/src/utils/download.js` — File download logic

---

## ARCHITECTURE SIGN-OFF

**This architecture is ready for implementation once approved.**

No coding yet. This is the technical blueprint for V2 integration.
