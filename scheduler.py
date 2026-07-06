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
        low, medium, high = [], [], []

        for task in self.tasks:                    # ← 1. loop over the tasks
            if task.priority == Priority.LOW:      # ← 2. task (instance) + Priority.LOW
                low.append(task)                   # ← 3. put the TASK into the bucket
            elif task.priority == Priority.MEDIUM:
                medium.append(task)
            else:
                high.append(task)
        return high + medium + low                 # ← 4. HIGH first

    

    def build_plan(self):
        """Keep tasks that fit the available time (high priority first) and drop the rest."""
        ordered = self.sort_by_priority()      # high → low
        remaining = self.owner.available_minutes
        scheduled = []
        dropped = []

        for task in ordered:
            if task.duration <= remaining:
                reason = "duration fits in the scheduled time"
                scheduled.append(ScheduledTask(task, reason))
                
                remaining -= task.duration

            else:
                dropped.append(task)
        total = self.owner.available_minutes - remaining
        return Plan(scheduled, dropped, total)
    

    

