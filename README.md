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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
tests/test_pawpal.py::test_mark_complete_changes_status PASSED                                                                                          [ 50%]
tests/test_pawpal.py::test_add_task_increases_count PASSED

```

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
