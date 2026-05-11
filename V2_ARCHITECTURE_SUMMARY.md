# PREMIUM MINI V2 — ARCHITECTURE SUMMARY

**Status:** PLANNING ONLY (No coding)  
**Production V1:** UNTOUCHED (remains live)  
**V2 Flow:** Parallel, opt-in, testing ready

---

## THE PARALLEL FLOWS

### PRODUCTION V1 (Current, Unchanged)
```
POST /api/moremindmap/mini-profile
→ scoreAssessment
→ generateMiniProfile (thin JSON)
→ Return: 16 JSON fields (~1,172 words)
→ Frontend renders
```

**Users see:** Basic behavioral text (current experience)

---

### PREMIUM V2 (New, Parallel)
```
POST /api/moremindmap/mini-profile-v2
→ scoreAssessment (reuse)
→ [Queue async job, return jobId immediately]
→ [Background worker runs:]
    - GPT-5.5 dense narratives (8-15 sec)
    - Doctrine filter clean prose
    - Generate signature codes
    - Build Page 2 system map
    - Render 18-page HTML
    - Save to storage
→ Return: download URL + status
→ Frontend polls for completion
→ User downloads premium report
```

**Users see:** Dense 18-page professional report with design elements

---

## KEY ARCHITECTURAL DECISIONS

### 1. Output Format Decision: **ASYNC + DOWNLOAD URL** (Recommended)

**Why async:**
- GPT calls take 8-15 seconds
- Users expect <2 sec response
- Production load requires non-blocking
- Can show progress UI ("Generating...")

**Why download URL:**
- Reduces response payload size
- User triggers download when ready
- Browser handles file management
- Can generate PDF server-side if needed

---

### 2. New Backend Files Required (5 files)

| File | Purpose |
|------|---------|
| `generatePremiumMiniProfileV2.js` | Main orchestrator (200-300 lines) |
| `signatureCodeGenerator.js` | Code conversion logic (50-100 lines) |
| `behavioralSystemMapBuilder.js` | Page 2 map data structure (100-150 lines) |
| `jobs/generateMiniReportV2.js` | Async job handler (150-200 lines) |
| `api/miniProfileV2Routes.js` | Route definitions (80-120 lines) |

**Total new code:** ~800-1,000 lines

---

### 3. Modified Backend Files (Minimal)

| File | Change |
|------|--------|
| `server.js` | Add V2 route (10-20 lines) |
| `package.json` | Add Bull/Redis if using queue |

---

### 4. Frontend Changes (Minimal)

| File | Change |
|------|--------|
| `MiniProfileForm.jsx` | Add V2 endpoint (5 lines) |
| `api.js` | V2 API call (15 lines) |
| `useMiniProfileV2.js` | State management (50 lines) |
| `download.js` | Download logic (20 lines) |

**Total frontend code:** ~100 lines

---

### 5. GPT-5.5 Integration

**Where it lives:** `generatePremiumMiniProfileV2.js`  
**What it does:** Generate 3,912-word dense narratives from scoring context  
**Token budget:** ~4K input + ~6K output per report  
**Cost:** ~$0.02 per report (GPT-4o-mini pricing)  
**Speed:** 8-15 seconds per call  

---

### 6. Doctrine Filter Integration

**Where:** After GPT call, before rendering  
**What:** Remove raw decimals, validate prose quality  
**If missing:** Locate `mindMapDoctrineFilter.js` or create minimal version  

---

### 7. Signature Codes Integration

**Where:** `signatureCodeGenerator.js` (new file)  
**What:** Convert 35.9/100 → V8, 17.9/100 → Fd4, etc.  
**Used by:** Cover page rendering  

---

### 8. HTML Renderer Integration

**Source:** `/moremindmap/utils/htmlRendererV5-PassA-Fixed.js` (existing)  
**Location in V2:** Port to backend, import as module  
**Input:** Complete payload (narratives, scores, codes, map data)  
**Output:** 18-page HTML string (45KB+)  

---

### 9. Generation Timeline

| Step | Time |
|------|------|
| Parse request | 10ms |
| Score assessment | 50ms |
| **GPT-5.5 call** | **8-15 sec** ← Bottleneck |
| Doctrine filter | 100ms |
| Signature codes | 10ms |
| Map builder | 20ms |
| HTML rendering | 100-200ms |
| File storage | 50ms |
| **TOTAL** | **8-15 sec** |

**Solution:** Async job queue handles long wait

---

### 10. Data Flow (Simplified)

```
User submits form (24 answers)
        ↓
POST /mini-profile-v2
        ↓
Receive & queue job
        ↓
Return jobId immediately (user doesn't wait)
        ↓
Background worker:
  - Score answers
  - Call GPT-5.5
  - Filter & clean
  - Generate codes
  - Build map
  - Render HTML
  - Save file
        ↓
User polls status endpoint
        ↓
When done, return download URL
        ↓
User downloads 18-page PDF/HTML report
```

---

## SAFETY (Production-Ready)

| Concern | Mitigation |
|---------|-----------|
| **GPT rate limits** | Queue with backoff |
| **Long wait time** | Async + show progress |
| **Storage bloat** | 24-hour TTL, auto-cleanup |
| **API key leaks** | .env only, never hardcoded |
| **User confusion** | Clear V1 vs V2 labels |
| **Fallback** | Return V1 JSON if GPT fails |

---

## ROLLOUT STRATEGY

### Phase 1: Internal Testing
- Deploy on dev branch
- Test with team submissions
- Validate output quality
- Profile generation time

### Phase 2: Beta (Feature Flag)
- Deploy behind feature flag
- Offer "Premium Report" to select users
- Collect feedback
- Monitor costs

### Phase 3: Production
- Remove feature flag
- All users access V2
- Keep V1 as fallback
- Monitor performance

### Phase 4: Deprecation (Future)
- Retire V1
- Archive old code

---

## FILES & LOCATIONS

### To Create (Backend)
```
/moremindmap-backend/engine/generatePremiumMiniProfileV2.js
/moremindmap-backend/engine/signatureCodeGenerator.js
/moremindmap-backend/engine/behavioralSystemMapBuilder.js
/moremindmap-backend/jobs/generateMiniReportV2.js
/moremindmap-backend/api/miniProfileV2Routes.js
```

### To Port (Backend)
```
/moremindmap/utils/htmlRendererV5-PassA-Fixed.js → Backend module
```

### To Modify (Backend)
```
/moremindmap-backend/server.js (add route line)
/moremindmap-backend/package.json (add deps if async)
```

### To Modify (Frontend)
```
/moremindmap/src/components/MiniProfileForm.jsx
/moremindmap/src/services/api.js
/moremindmap/src/hooks/useMiniProfileV2.js
/moremindmap/src/utils/download.js
```

---

## NEXT: IMPLEMENTATION

**When approved, these steps follow (in this order):**

1. Create new backend files
2. Implement GPT prompt
3. Wire doctrine filter
4. Add signature code logic
5. Build map data generator
6. Set up job queue (Bull/Redis)
7. Frontend integration
8. End-to-end testing
9. Deploy to production

**No changes to production V1 during any phase.**

---

## ARCHITECTURE IS READY FOR CODING

This is the blueprint. All design decisions are locked.

Ready to proceed when approved.
