# V2 ARCHITECTURE — LOCKED & READY (NO CODING YET)

**Date:** 2026-05-04 10:00 MST  
**Status:** ✅ **PLANNING COMPLETE**  
**Next Phase:** Implementation (requires separate approval)

---

## PRODUCTION V1 STATUS

| Component | Status | Change | Risk |
|-----------|--------|--------|------|
| `/api/moremindmap/mini-profile` | LIVE | ✅ NONE | None |
| `scoreAssessment.js` | LIVE | ✅ NONE | None |
| `miniProfileGenerator.js` | LIVE | ✅ NONE | None |
| `server.js` | LIVE | ⏳ Add route only | Low |
| Frontend forms | LIVE | ⏳ Add V2 option | None |

**Confirmation:** Production V1 remains 100% untouched. V2 is pure addition.

---

## V2 ARCHITECTURE SUMMARY

### Endpoint
```
POST /api/moremindmap/mini-profile-v2
```

### Input
```
24 answers (same structure as V1)
```

### Output Decision
```
Async response: { jobId, statusUrl }
Polling endpoint: GET /api/mini-profile-v2/status/:jobId
Final response: { status: "complete", downloadUrl, filesize }
Download: HTML or PDF report (18 pages, 45KB+)
```

### Processing Pipeline
```
1. Parse & validate (10ms)
2. Score assessment [REUSE V1] (50ms)
3. Queue async job (immediate)
4. Background worker runs:
   - GPT-5.5 dense narratives (8-15 sec) ← BOTTLENECK
   - Doctrine filter clean (100ms)
   - Signature codes generate (10ms)
   - System map data build (20ms)
   - HTML render (100-200ms)
   - File storage (50ms)
5. Poll returns download URL
```

### Generation Time
```
Total: 8-15 seconds (GPT-5.5 bottleneck)
Solution: Async job queue with status polling
```

---

## NEW FILES TO CREATE

```
/backend/engine/generatePremiumMiniProfileV2.js     [200-300 lines]
/backend/engine/signatureCodeGenerator.js           [50-100 lines]
/backend/engine/behavioralSystemMapBuilder.js       [100-150 lines]
/backend/jobs/generateMiniReportV2.js               [150-200 lines]
/backend/api/miniProfileV2Routes.js                 [80-120 lines]
Total: ~800-1,000 lines new backend code
```

---

## FILES TO MODIFY (MINIMAL)

```
/backend/server.js                [+10-20 lines: add route]
/backend/package.json             [+deps if async]
/frontend/MiniProfileForm.jsx      [+5 lines]
/frontend/services/api.js          [+15 lines]
/frontend/hooks/useMiniProfileV2.js [+50 lines]
/frontend/utils/download.js        [+20 lines]
Total: ~100 lines frontend, 30 lines backend modifications
```

---

## FILES TO PORT/REUSE

```
/moremindmap/utils/htmlRendererV5-PassA-Fixed.js → Backend module
/moremindmap-backend/engine/scoreAssessment.js    → Reuse as-is
```

---

## INTEGRATION POINTS (Exact)

### 1. GPT-5.5 Call
**File:** `generatePremiumMiniProfileV2.js` (new)  
**Timing:** After scoring, before filtering  
**Input:** Scoring object  
**Output:** 12 narrative sections  

### 2. Doctrine Filter
**File:** `mindMapDoctrineFilter.js` (locate or create)  
**Timing:** After GPT, before rendering  
**Input:** Raw narratives  
**Output:** Clean narratives  

### 3. Signature Codes
**File:** `signatureCodeGenerator.js` (new)  
**Timing:** After GPT, parallel with filter  
**Input:** Normalized scores  
**Output:** Code object (V8, Fd4, F4, etc.)  

### 4. System Map Builder
**File:** `behavioralSystemMapBuilder.js` (new)  
**Timing:** After signatures, parallel with rendering  
**Input:** Pattern structure  
**Output:** Map data JSON  

### 5. HTML Renderer
**File:** `htmlRendererV5-PassA-Fixed.js` (port to backend)  
**Timing:** Last step before file storage  
**Input:** All components (narratives, codes, scores, map)  
**Output:** 18-page HTML string  

---

## ASYNC JOB QUEUE (RECOMMENDED)

### Technology
```
Bull Queue with Redis backend
(or simple in-memory queue if MVP)
```

### Implementation
```
- Endpoint returns immediately with jobId
- Job queues in background
- Frontend polls status endpoint
- When done, returns download URL
- User downloads report
```

### Advantages
```
✅ Non-blocking user experience
✅ Handles concurrent requests
✅ Survives server restarts (with Redis)
✅ Production-grade architecture
✅ Can add retries/backoff
```

---

## ROLLOUT PHASES

### Phase 1: Internal Testing
- Deploy on dev branch
- Test suite completion
- Output quality validation
- Performance profiling

### Phase 2: Beta (Feature Flag)
- Deploy behind feature flag
- Offer "Premium Report" option
- Select user group testing
- Feedback collection

### Phase 3: Production Rollout
- Remove feature flag
- All users see V2 option
- Keep V1 as fallback
- Monitor metrics

### Phase 4: Deprecation (Future)
- Retire V1 (if desired)
- Archive old code

---

## SAFETY CHECKLIST

- [ ] Production V1 endpoint unchanged
- [ ] V1 scoring logic reused unchanged
- [ ] V1 users unaffected
- [ ] V2 is opt-in (feature flag)
- [ ] Async prevents timeouts
- [ ] Job queue handles concurrency
- [ ] GPT API errors gracefully degrade to V1
- [ ] Rate limiting in place
- [ ] Storage cleanup (24-hour TTL)
- [ ] API keys in .env only
- [ ] No hardcoded credentials

---

## DECISION MATRIX

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Output format** | Async + download URL | Non-blocking, scalable |
| **File type** | HTML primary, PDF optional | Browser-native, easy share |
| **Report length** | 18 pages (expanded) | No clipping, full content |
| **Word density** | 3,912 words (premium) | GPT-5.5 quality |
| **Design elements** | Page 2 map, signature codes | Professional instrument feel |
| **Fallback strategy** | Return V1 JSON on GPT failure | Graceful degradation |
| **User experience** | Progress UI during generation | Transparency, no confusion |

---

## ESTIMATION

### Backend Development
```
New files: 5 × 40-60 hours = 200-300 hours
Modifications: 10-20 hours
Testing: 20-40 hours
Total Backend: ~250 hours
```

### Frontend Development
```
New components: 15 hours
API integration: 10 hours
Testing: 10 hours
Total Frontend: ~35 hours
```

### DevOps/Infrastructure
```
Job queue setup: 5-10 hours
Deployment config: 5 hours
Monitoring setup: 5 hours
Total: ~15 hours
```

### TOTAL PROJECT ESTIMATE
```
Development: 250-350 hours
Testing/QA: 40-60 hours
Deployment: 20-30 hours
TOTAL: 310-440 hours (~8-11 weeks, 1 engineer)
```

---

## RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| GPT API quota exceeded | Medium | High | Implement rate limiting, queue backoff |
| Long generation time | High | Medium | Async + progress UI expected |
| Storage bloat | Low | Medium | 24-hour TTL, auto-cleanup |
| User confusion (V1 vs V2) | Medium | Low | Clear UI labeling |
| Frontend doesn't support new format | Low | High | Include frontend changes in plan |
| Production downtime | Very Low | Critical | Feature flag + V1 fallback |

---

## SIGN-OFF CHECKLIST

### Architecture Planning
- [x] V1 endpoint identified
- [x] V2 endpoint designed
- [x] Data flow mapped
- [x] Files identified (new, modified, ported)
- [x] Async strategy chosen
- [x] Integration points documented
- [x] Safety measures defined
- [x] Rollout phases planned

### Ready for Implementation
- [x] No production changes in plan
- [x] V2 is pure addition
- [x] All components identified
- [x] No blocking dependencies
- [x] All risks documented
- [x] Fallback strategy in place

---

## DOCUMENTS CREATED

1. ✅ `/V2_ARCHITECTURE.md` (18,863 bytes) — Complete technical blueprint
2. ✅ `/V2_ARCHITECTURE_SUMMARY.md` (6,355 bytes) — Executive summary
3. ✅ `/ARCHITECTURE_LOCKED_NOCODE.md` (this document) — Lock & confirmation

---

## APPROVAL GATE

**This architecture is complete and ready for implementation approval.**

Next step: Technical review + greenlight to code.

**No coding will proceed until explicit approval is given.**

**Production V1 remains untouched throughout planning and implementation.**

---

## LOCKED FOR REFERENCE

**Locked on:** 2026-05-04 10:00 MST  
**Status:** ✅ NO CODING YET  
**Production:** ✅ SAFE  
**Next Gate:** Implementation approval  

Ready to build when authorized.
