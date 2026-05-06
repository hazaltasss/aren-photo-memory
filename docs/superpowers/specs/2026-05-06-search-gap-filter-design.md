# Search Improvement — Dynamic Gap Filter

## Problem

`gemini-embedding-2` produces cosine distances in the `0.65–0.85` range, far above the `0.0–0.5` range assumed by the original threshold. Any fixed cutoff is model-specific and breaks when the model changes.

## Solution

Replace the static `SEARCH_THRESHOLD` with a **gap filter** applied in Python after fetching top-N results:

1. Fetch top-N results ordered by distance (no WHERE filter)
2. Find the best (lowest) distance
3. Drop any result whose distance exceeds `best_distance + SEARCH_GAP`
4. Return remaining results with a `relevance` score (1 - distance, as a 0–100 percentage)

This is model-agnostic and self-calibrating.

## Changes

### `backend/.env` + `backend/.env.example`
- Remove: `SEARCH_THRESHOLD`
- Add: `SEARCH_GAP=0.08` (max allowed distance delta from best match)
- Add: `SEARCH_LIMIT=20` (moved from hardcoded default in router)

### `backend/app/config.py`
- Remove: `SEARCH_THRESHOLD: float`
- Add: `SEARCH_GAP: float`
- Add: `SEARCH_LIMIT: int`

### `backend/app/routers/search.py`
- SQL: Remove `WHERE distance < ?` subquery filter — fetch all, ordered by distance, limit by `SEARCH_LIMIT`
- Python: Apply gap filter post-fetch
- Response: Include `relevance` (int 0–100) in results

### `backend/app/schemas.py`
- Add `relevance: int` field to `PhotoResponse`

### `frontend/src/api/client.ts`
- Add `relevance: number` to `Photo` interface

### `frontend/src/pages/Gallery.tsx`
- Show relevance badge on search results (only when search is active, not in gallery mode)

## Success Criteria
- "mutlu çocuk" returns the relevant photo(s) ✅
- "uzay gemisi" returns empty list ✅  
- Works regardless of embedding model used ✅
- No hardcoded values anywhere ✅
