# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.



## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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

## 🖥️ Sample Output

Running `python main.py` with an owner who has 60 minutes available and three tasks
(Morning walk 30m/high, Meds 10m/high, Grooming 25m/low) produces:

```
I scheduled Morning walk because duration fits in the scheduled time, it takes 30 minutes
I scheduled Meds because duration fits in the scheduled time, it takes 10 minutes
I dropped Grooming — not enough time left
Total time used: 40 minutes
```

The two high-priority tasks (30 + 10 = 40 min) are scheduled first; grooming is dropped
because only 20 minutes remain and it needs 25.

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
