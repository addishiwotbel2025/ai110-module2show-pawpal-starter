# PawPal+ 🐾

**PawPal+** is a pet care planning assistant. It helps a busy pet owner stay consistent
with care by turning a list of tasks — walks, feeding, meds, grooming, enrichment — into
a clear daily plan that respects the time they actually have, and explains every choice.

It runs as an interactive **Streamlit app** and as a small **command-line demo**.

## ✨ Features

- **Priority sorting** — orders tasks HIGH → MEDIUM → LOW so the most important care is
  planned first (`Scheduler.sort_by_priority`).
- **Sorting by time** — orders tasks chronologically by start time, with flexible
  (no fixed time) tasks placed last (`Scheduler.sort_by_time`).
- **Time-budget planning** — fits tasks into the owner's available minutes, highest
  priority first, and drops what doesn't fit (`Scheduler.build_plan`).
- **Conflict warnings** — detects tasks whose fixed times overlap and warns the owner;
  the schedule keeps the higher-priority task and drops the clash
  (`Scheduler.conflicts`, `Scheduler.find_conflicts`).
- **Filtering by status** — completed tasks are skipped when building a new plan
  (`Scheduler.pending`).
- **Filtering by pet** — narrows tasks to a single pet for multi-pet households
  (`Scheduler.for_pet`).
- **Recurring tasks** — once / daily / weekly recurrence; completing a recurring task
  automatically queues its next occurrence (`Task.frequency`, `Task.next_occurrence`,
  `Pet.complete_task`, `Scheduler.tasks_for_day`).
- **Explainable plans** — every scheduled or dropped task comes with a plain-English
  reason (`Plan.explain`).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧪 Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest
```

### What the tests cover

The suite in [`tests/test_pawpal.py`](tests/test_pawpal.py) has **17 tests** across
the core behaviors, covering both happy paths and edge cases:

- **Basics** — a task can be marked complete; adding a task grows the pet's list.
- **Sorting** — `sort_by_time()` returns tasks in chronological order and pushes
  flexible (no fixed time) tasks to the end; `sort_by_priority()` returns HIGH → LOW.
- **Filtering** — `pending()` excludes completed tasks; `for_pet()` returns only a
  given pet's tasks.
- **Conflict detection** — overlapping times are flagged, including **two tasks at
  the exact same time**; back-to-back tasks do *not* conflict; flexible tasks never
  conflict.
- **Recurrence** — completing a **daily** task creates a fresh task for the next day;
  a **once** task does not recur; `tasks_for_day()` returns the right tasks per weekday.
- **Plan building (edge cases)** — an empty task list yields an empty plan (no crash);
  an over-budget task is dropped ("not enough time left"); a conflicting task is
  dropped in favor of the higher-priority one.

### Successful run

```
collected 17 items

tests/test_pawpal.py .................                                   [100%]

============================== 17 passed in 0.01s ==============================
```

### Confidence Level: ⭐️⭐️⭐️⭐️☆ (4 / 5)

The four core behaviors (sorting, filtering, conflict detection, recurrence) are
each covered by direct tests plus edge cases, and all 17 pass. Docking one star
because a few areas are still untested/incomplete: weekly recurrence relies on a
manually set `Task.weekday`, `build_plan()` doesn't yet lay tasks on a real clock
(it treats the day as a pool of minutes), and owner preferences aren't used yet.

## 📐 Smarter Scheduling

Most of what used to feel *manual* came from one gap: a `Task` only knew its
`title`, `duration`, `priority`, and `completed` status. Adding a start time
(`fixed_time`) and a `frequency` to `Task` unlocked the four features below.

| Feature | Method(s) | Status |
|---------|-----------|--------|
| Sorting by priority | `Scheduler.sort_by_priority()` | ✅ Implemented |
| Sorting by time | `Scheduler.sort_by_time()` | ✅ Implemented |
| Filtering by completion status | `Scheduler.pending()` | ✅ Implemented |
| Filtering by pet | `Scheduler.for_pet(pet)` | ✅ Implemented |
| Conflict detection | `Scheduler.conflicts(a, b)`, `Scheduler.find_conflicts()` | ✅ Implemented |
| Recurring tasks | `Task.frequency`, `Task.weekday`, `Scheduler.tasks_for_day(weekday)` | ✅ Implemented (once / daily / weekly) |

### Sorting

- **`Scheduler.sort_by_priority()`** — returns tasks ordered HIGH → MEDIUM → LOW.
  Uses a dict-bucket sort (one bucket per `Priority` member, then walk the enum
  by `.value` descending). This is O(n) and needs zero changes if a new priority
  level is added to the enum.
- **`Scheduler.sort_by_time()`** — returns tasks in chronological order by
  `Task.start_minutes()` (minutes past midnight). Flexible tasks with no
  `fixed_time` sort to the end instead of crashing.

### Filtering

- **`Scheduler.pending()`** — returns only tasks where `completed == False`, so
  finished tasks don't get re-scheduled.
- **`Scheduler.for_pet(pet)`** — returns only the tasks belonging to a given pet,
  for multi-pet households.

### Conflict detection

- **`Scheduler.conflicts(a, b)`** — two fixed-time tasks overlap when
  `a.start < b.end and b.start < a.end` (compared in minutes). Flexible tasks
  (no `fixed_time`) never conflict.
- **`Scheduler.find_conflicts()`** — sorts fixed-time tasks by start, then
  compares each task only to its neighbor, so overlaps are found in O(n) after
  the sort. `build_plan()` uses this logic to drop a task that overlaps one
  already scheduled (the higher-priority task wins), and `Plan.explain()` reports
  it, e.g. `I dropped Meds — it overlaps with Walk`.

### Recurring tasks

- **`Task.frequency`** — `"once"`, `"daily"`, or `"weekly"`.
- **`Task.weekday`** — for weekly tasks, the day they recur on (0=Mon … 6=Sun).
- **`Scheduler.tasks_for_day(weekday)`** — returns the tasks active on a given day:
  `daily` tasks always, `once` tasks only until they're completed, and `weekly`
  tasks only when their `weekday` matches the requested day.

## 📸 Demo Walkthrough

PawPal+ runs two ways: an interactive **Streamlit app** and a quick **command-line demo**.

```bash
streamlit run app.py     # interactive UI
python main.py           # command-line demo
```

### Main UI features

The Streamlit app is a single page. From top to bottom, a user can:

1. **Enter owner & pet info** — owner name, pet name/species, and the minutes available
   for care today.
2. **Add tasks** — each task has a title, duration, and priority, plus an *optional*
   fixed start time and a recurrence (once / daily / weekly; weekly asks which weekday).
3. **Review current tasks** — a table of all tasks **sorted by start time**, with a live
   **conflict warning** whenever two fixed-time tasks overlap.
4. **Complete a task** — marking a daily/weekly task done automatically queues its next
   occurrence.
5. **Generate the schedule** — builds the day's plan and shows *Scheduled / Time used /
   Time left* metrics, the ordered plan, and any dropped tasks with reasons.

### Example workflow

1. Enter owner **Jordan**, pet **Mochi** (cat), and **60** available minutes.
2. Add **Morning walk** — 20 min, high priority, starts **08:00**, **daily**.
3. Add **Meds** — 10 min, medium priority, starts **08:10**. The task table immediately
   shows a ⚠️ warning: *Morning walk (08:00) overlaps Meds (08:10)*.
4. Add **Grooming** — 30 min, low priority, no fixed time (flexible).
5. Click **Generate schedule**. The plan shows:
   - ✅ **Morning walk** and **Grooming** scheduled — **50 of 60** minutes used, 10 left.
   - ⚠️ **Meds dropped** — *it overlaps with Morning walk* (the higher-priority walk wins).
6. Mark **Morning walk** complete → a fresh, uncompleted "Morning walk" is queued for the
   next day, demonstrating daily recurrence.

### Key Scheduler behaviors shown

- **Sorting** — the task table and the final plan are shown in time order; the plan itself
  is built highest-priority-first (`sort_by_priority` / `sort_by_time`).
- **Conflict warnings** — overlapping fixed-time tasks are flagged before scheduling, and
  the lower-priority task is dropped with an explanation (`find_conflicts` / `build_plan`).
- **Filtering** — completed tasks are excluded from new plans (`pending`).
- **Recurrence** — completing a daily/weekly task rolls it over to the next day
  (`complete_task` / `next_occurrence`).

### Command-line demo output

Running `python main.py` (owner with 60 minutes; a 30-min high-priority walk and a 10-min
high-priority meds task) prints the explained plan:

```
I scheduled Morning walk because duration fits in the scheduled time, it takes 30 minutes
I scheduled Meds because duration fits in the scheduled time, it takes 10 minutes
Total time used: 40 minutes
```
