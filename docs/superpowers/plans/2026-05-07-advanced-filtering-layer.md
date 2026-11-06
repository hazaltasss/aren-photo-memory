# Advanced Filtering Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a hybrid search engine and horizontal filter bar for Aren Photo Memory.

**Architecture:** Unified Search Engine (Vector + SQL). The backend will combine semantic similarity with structured metadata filters. The frontend will feature a horizontal glassmorphism filter bar.

**Tech Stack:** FastAPI, SQLite (sqlite-vec), React, Tailwind CSS.

---

### Task 1: Backend - Filter Options & Schema Update

**Files:**
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/routers/search.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Update SearchRequest schema**
  Add a `filters` object to `SearchRequest` in `backend/app/routers/search.py`.
  ```python
  class SearchFilters(BaseModel):
      emotions: Optional[List[str]] = None
      location_types: Optional[List[str]] = None
      objects: Optional[List[str]] = None
      hair_length: Optional[str] = None
      # date_range: Optional[dict] = None # Later

  class SearchRequest(BaseModel):
      query: Optional[str] = None
      filters: Optional[SearchFilters] = None
      limit: int = 20
  ```

- [ ] **Step 2: Create Filter Options Endpoint**
  Create a new router `backend/app/routers/filters.py` with an endpoint `/api/filters/options` that returns unique emotions, locations, and top 10 objects from the DB.
  ```python
  @router.get("/options")
  def get_filter_options():
      conn = get_db_connection()
      cursor = conn.cursor()
      # Get unique emotions, locations, and top objects
      # Return as {emotions: [], locations: [], objects: []}
  ```

- [ ] **Step 3: Register the new router in main.py**
- [ ] **Step 4: Commit**
  `git add . && git commit -m "feat(backend): add filter options endpoint and update search schema"`

---

### Task 2: Backend - Hybrid Search Implementation

**Files:**
- Modify: `backend/app/routers/search.py`

- [ ] **Step 1: Update search_photos logic**
  Modify the SQL query generation to dynamically append `WHERE` clauses based on `req.filters`.
  If `query` is present, it uses `vec_distance_cosine` as before, but with additional `AND` filters.
  If `query` is absent, it's a pure SQL metadata search.

- [ ] **Step 2: Test with curl**
  Test a combined search: `curl -X POST -H "Content-Type: application/json" -d '{"query": "park", "filters": {"emotions": ["mutlu"]}}' http://localhost:8000/api/search`

- [ ] **Step 3: Commit**
  `git commit -m "feat(backend): implement hybrid semantic-SQL search logic"`

---

### Task 3: Frontend - FilterBar UI & Logic

**Files:**
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/pages/Gallery.tsx`

- [ ] **Step 1: Update API Client**
  Add `getFilterOptions` query and update `searchPhotos` mutation signature to accept the new filter object.

- [ ] **Step 2: Implement FilterBar Component**
  Inside `Gallery.tsx`, add a horizontal bar with popovers for each category.
  Implement the "Objects" filter with top chips + input field.

- [ ] **Step 3: Connect State**
  Ensure that changing a filter triggers a new search.

- [ ] **Step 4: Commit**
  `git commit -m "feat(frontend): add horizontal filter bar and connect to backend API"`

---

### Task 4: Final Polish & Verification

- [ ] **Step 1: Visual Refinement**
  Ensure glassmorphism and animations match the premium design.
- [ ] **Step 2: E2E Verification**
  Verify that "Happy" filter works correctly with "park" search.
- [ ] **Step 3: Commit & Cleanup**
  `git commit -m "style: final polish of the advanced filtering layer"`
