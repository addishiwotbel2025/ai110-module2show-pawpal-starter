from enum import Enum
from datetime import time

class Pet:
    """A pet and the list of care tasks that belong to it."""
    def __init__(self, name, age, breed, species):
        self.name = name
        self.age = age
        self.breed = breed
        self.species = species
        self.tasks = []

    def add_task(self, task):
        """Add a Task to this pet's list of care tasks."""
        self.tasks.append(task)

    def complete_task(self, task):
        """Mark a task complete; if it recurs, add its next occurrence.

        Returns the newly created next task (or None for one-time tasks).
        """
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            self.tasks.append(upcoming)
        return upcoming

# priority is not recommended here, becuase it becomes confusing
# changed name from availability to availabile_minutes.
class Owner:
    """A pet owner and how many minutes they have available for care."""
    #  preferences = None
    def __init__(self, name, available_minutes):
        self.name = name
        self.available_minutes = available_minutes
        # self.preferences = {}


class Task:
    """A single care task with a duration, priority, and completion status."""
    # category, fixed_time = None
    def __init__(self, title, duration, priority, fixed_time = None,
                 frequency = "once", weekday = None):
        self.title = title
        self.duration = duration
        self.priority = priority
        self.fixed_time = fixed_time
        # how frequently a task occurs: "once" | "daily" | "weekly"
        self.frequency = frequency
        # for weekly tasks, which day it recurs on (0=Mon … 6=Sun); None otherwise
        self.weekday = weekday
        self.completed = False
        
    def start_minutes(self):
            """Start time as minutes past midnight; None if the task is flexible."""
            if self.fixed_time is None:
                return None
            return self.fixed_time.hour * 60 + self.fixed_time.minute

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self):
        """Return a fresh, uncompleted copy of this task for its next recurrence.

        Daily and weekly tasks come back for their next day; one-time ("once")
        tasks do not recur, so this returns None for them.
        """
        if self.frequency == "once":
            return None
        return Task(
            self.title, self.duration, self.priority,
            self.fixed_time, self.frequency, self.weekday,
        )
        

class Priority(Enum):
    """Fixed priority levels a task can have."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
#ScheduledTask -> Task
class ScheduledTask:
    """A task that made it into the plan, plus the reason it was scheduled."""
    # start_time
    def __init__(self, task, reason):
        self.task = task
        # self.start_time = start_time
        self.reason = reason


class Plan:
    """The result of scheduling: what was scheduled, what was dropped, and total time."""
    def __init__(self, scheduled, dropped, total_minutes):
        self.scheduled = scheduled
        self.dropped = dropped
        self.total_minutes  = total_minutes

    def explain(self):
        """Return a readable summary of scheduled/dropped tasks and total time."""
        lines = []
        for st in self.scheduled:
            lines.append(
                f"I scheduled {st.task.title} because {st.reason}, "
                f"it takes {st.task.duration} minutes"
            )
        for task, reason in self.dropped:
            lines.append(f"I dropped {task.title} — {reason}")
        lines.append(f"Total time used: {self.total_minutes} minutes")
        return "\n".join(lines)


