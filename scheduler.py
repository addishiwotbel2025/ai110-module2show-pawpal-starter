from models import Owner, Pet, Task, Priority, ScheduledTask, Plan


'''
   class Scheduler {
        +Owner owner
        +Pet pet
        +list~Task~ tasks
        +build_plan() Plan
        +sort_by_priority() list~Task~
    }
'''
class Scheduler:
    """Builds a daily care plan from an owner's available time and a task list."""
    def __init__(self, owner, tasks):
        self.owner = owner
        self.tasks = tasks

    def sort_by_priority(self):
        """Return the tasks ordered high to low priority."""
        buckets = {p: [] for p in Priority}        # one bucket per priority level
        for task in self.tasks:
            buckets[task.priority].append(task)    # O(1) placement into its bucket
        ordered = []
        for p in sorted(Priority, key=lambda p: p.value, reverse=True):  # HIGH → LOW
            ordered.extend(buckets[p])
        return ordered

    def sort_by_time(self):
        """Tasks in chronological order; flexible (None) tasks go last."""
        return sorted(
            self.tasks,
            key=lambda t: (t.start_minutes() is None, t.start_minutes() or 0)
    )

    def pending(self):
        """Return only the tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def for_pet(self, pet):
        """Return only the tasks that belong to the given pet."""
        return [t for t in self.tasks if t in pet.tasks]
    def conflicts(self, a, b):
        """True if two fixed-time tasks overlap."""
        a_start, b_start = a.start_minutes(), b.start_minutes()
        if a_start is None or b_start is None:
            return False                      # flexible tasks can't clash
        a_end, b_end = a_start + a.duration, b_start + b.duration
        return a_start < b_end and b_start < a_end

    def find_conflicts(self):
        """All overlapping pairs. Sort by start first, then compare neighbors."""
        fixed = [t for t in self.sort_by_time() if t.start_minutes() is not None]
        clashes = []
        for i in range(len(fixed) - 1):
            if self.conflicts(fixed[i], fixed[i + 1]):
                clashes.append((fixed[i], fixed[i + 1]))
        return clashes

    def tasks_for_day(self, weekday):
        """weekday: 0=Mon … 6=Sun. Returns tasks active on that day."""
        result = []
        for t in self.tasks:
            if t.frequency == "daily":
                result.append(t)
            elif t.frequency == "weekly":
                # weekly tasks recur only on their assigned day
                if t.weekday == weekday:
                    result.append(t)
            else:  # "once" — a one-time task, keep it only until it's done
                if not t.completed:
                    result.append(t)
        return result

    def build_plan(self):
        """Build a daily plan, scheduling tasks high priority first.

        A task is dropped if it overlaps a task already scheduled (time conflict)
        or if its duration no longer fits the owner's remaining minutes. Each
        dropped entry is a (task, reason) pair so the plan can explain the drop.
        """
        ordered = self.sort_by_priority()      # high → low
        remaining = self.owner.available_minutes
        scheduled = []
        dropped = []

        for task in ordered:
            # first task already scheduled that this one overlaps in time, if any
            clash = next(
                (s.task for s in scheduled if self.conflicts(task, s.task)),
                None,
            )
            if clash is not None:
                dropped.append((task, f"it overlaps with {clash.title}"))
            elif task.duration <= remaining:
                scheduled.append(ScheduledTask(task, "duration fits in the scheduled time"))
                remaining -= task.duration
            else:
                dropped.append((task, "not enough time left"))
        total = self.owner.available_minutes - remaining
        return Plan(scheduled, dropped, total)
    

    

