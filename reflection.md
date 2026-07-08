# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
my initial UML design has classes 
    pet 
    owner
    task
    priority - ranks priority ad high, medium and low
    scheduled task - is an object that holds a task and a reason for why it is either added or not added



- What classes did you include, and what responsibilities did you assign to each?
    pet and owner define basic attributes such as:
    pet - name, age, breed, species
    owner - name, available_minutes
    task - has the name, duration and priority level of a task
    priority just labels task as high, medium or low
    scheduled task carries tasks that are scheduled and reason for their scheduling
    
    plan - is used for a good display. it takes in a list of
        scheduled tasks
        dropped tasks
        and explanation for why they were either added or dropped.
        
You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

adding a pet
pet - object
    attributes:
        name
        age
        breed
        species

the person has a pet, adminsitrates a pet
person - object
    attributes:
        availability
        prefernces

pet care class:
    walking dog
        for how many minutes? threshold
    feeding dog
        how many calories? threshold
    giving medication
        what are the meds? does it even take one?
    grooming
        what time? 

class that basically calculates everything:
    claculates available hours using time availability form person class then returns amount of hours we need to spend doing activities for the dog

    drops tasks based on priority


person:
    working hours
    availability ( free time)
    pet care prefernces


have an owner_preference list that appends items from the 4 choices
log in amount of time and assign a percentage for each task




**b. Design changes**

- Did your design change during implementation?

Yes, in a few important ways:

- **`Task` grew.** It started as just `title`, `duration`, and `priority`. Once I
  wanted smarter scheduling I added `fixed_time`, `frequency`, `weekday`, and
  `completed`. Adding `fixed_time` was the single change that unlocked sorting by
  time, conflict detection, and preferences — everything else depended on it.
- **`Plan.dropped` changed shape.** It was a plain list of tasks; I changed it to a
  list of `(task, reason)` pairs so the plan could explain *why* something was
  dropped (out of time vs. time conflict), not just that it was.
- **Recurrence needed new behavior.** I added `Pet.complete_task()` and
  `Task.next_occurrence()` so that finishing a daily/weekly task automatically
  queues its next occurrence, instead of me re-adding it by hand.
- **Dropped the Owner→Pet link.** My first UML drew Owner "cares for" Pet directly.
  In code the `Owner` never needs a reference to the `Pet`; the `Scheduler` is what
  ties an owner's time budget to a task list, so I removed that arrow to match reality.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

My scheduler weighs four constraints:

1. **Time budget** — the owner's `available_minutes`. A task is only scheduled if its
   duration still fits the minutes left.
2. **Priority** — HIGH → MEDIUM → LOW. Priority decides the order tasks are considered
   and who wins when two tasks can't both happen.
3. **Time conflicts** — two tasks with overlapping fixed start times can't both run, so
   the lower-priority one is dropped.
4. **Completion status** — completed tasks are filtered out so they aren't re-scheduled.

(Owner *preferences* are stubbed in the design but not used in scheduling yet.)

- How did you decide which constraints mattered most?

Time and priority are the core. A plan that ignores the time you actually have is
useless, and once time runs out, priority is what tells you which tasks are worth
keeping. Conflicts and completion status are refinements on top of those two — they
make the plan realistic, but they only matter once the time-and-priority core works.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The tradeoff I thought about most was in `sort_by_priority()`: **time complexity
vs. readability vs. how much manual editing the code needs to grow.**

My first version used three named lists (`low`, `medium`, `high`), looped once
over the tasks dropping each into its bucket, and returned `high + medium + low`.
It was O(n) and fast, but it was 12 lines, and the ordering (`high + medium +
low`) was hand-written — if I ever added a new priority level, I'd have to edit
three separate places (a new list, a new `elif`, and the return line).

The obvious "readable" alternative was one line:
`sorted(self.tasks, key=lambda t: t.priority.value, reverse=True)`. Very clear,
and it scales to any number of priority levels for free — but sorting is
O(n log n).

I picked O(n) on principle when it's basically free, but I didn't want to pay for
it in readability. So I landed on a **dict-bucket** version: build one bucket per
`Priority` member, drop each task in with an O(1) lookup, then walk the priorities
in `.value` order. This keeps the O(n) placement of my original code AND scales
like the one-liner — adding an `URGENT` level to the enum needs zero changes here,
because the order now comes from the enum instead of a hand-written return line.

- Why is that tradeoff reasonable for this scenario?

Honestly, for a day's worth of pet tasks the O(n) vs. O(n log n) difference is
invisible — the list is tiny. So the real win wasn't raw speed; it was removing
the "edit three places to add a priority" tax while staying efficient. Choosing
the version that is both fast and low-maintenance means the code is less likely
to break or drift out of sync the next time I extend it, which matters more on a
small learning project than shaving microseconds.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project?

I used it to explain lines that I don't understand
When it recommends something, I ask why the recommendation is better than my initial plan
I use it to summarize my reflections, I give it an outline


- Which AI coding assistant features were most effective for building your scheduler?

Three stood out:

1. **Code review that actually runs the code.** The assistant caught that my
   `start_minutes()` method was accidentally nested *inside* `__init__` (an indentation
   slip) and *proved* it by running a snippet that raised `AttributeError`. That would
   have crashed sorting and conflict detection. 
   
2. **"Sketch, I code" mode.** Instead of dumping full implementations, I had it give me
   method signatures and small sketches, then I wrote the real code and it reviewed. I
   learned more and stayed in control of the design.
3. **Automated verification.** It ran `pytest` and drove the Streamlit app with
   `AppTest` to confirm features worked end-to-end, so "it works" was demonstrated, not
   claimed.

**b. Judgment and verification**

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

When simplifying `sort_by_priority()`, the assistant first recommended replacing my
three-bucket sort with a one-line `sorted(self.tasks, key=..., reverse=True)` "for
readability." I rejected that as-is because sorting is O(n log n) and I wanted to keep the
O(n) behavior of my original code. We modified the idea into a **dict-bucket sort** that is
both O(n) *and* extensible. I made the call that efficiency + low-maintenance mattered more
than the shortest possible line — the AI optimized for readability, but I owned the
priorities. (I also rejected its first draft of the Tradeoffs section because it documented
a different tradeoff than the one I actually wanted to highlight.)

- How did you evaluate or verify what the AI suggested?

I didn't take explanations on faith — I verified by running things. Logic changes were
checked with `pytest`, UI changes by actually launching/driving the app, and the demo
numbers in the README came from real executions, not from what the AI said would happen.
Reading the code myself mattered too: the indentation bug *looked* fine, so "it looks
right" was never enough.

**c. Working in phases / separate sessions**

- How did using separate chat sessions for different phases help you stay organized?

I kept each phase — design, implementation, testing, documentation — as its own focused
job. Scoping a session to one concern meant I (and the assistant) weren't mixing "is the
algorithm correct?" with "is this test right?" or "does the README read well?" at the same
time. Each phase started from a clear goal and ended with something verifiable (a passing
test, a working button, an updated doc), which made it easy to see progress and to hand the
next phase a clean starting point.

**d. Being the "lead architect"**

- Summarize what you learned about being the lead architect when collaborating with powerful AI tools.

I think it is something to lookout for because it can recommend ideas that seem incredible. However, if I don't understand what is going on, there is no way to track my progress or critique what it is recommending.

Also, it is good at explaining something that is not clear...and adding personal prompts is helpful
for example: give me a metaphor...

also, it made me realize that my code is not always perfect and there is always a tradeoff to make


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I wrote 17 tests in `tests/test_pawpal.py` across the four core behaviors:

- **Sorting** — chronological order, flexible (no-time) tasks sorted last, and priority
  order HIGH → LOW.
- **Filtering** — `pending()` excludes completed tasks; `for_pet()` returns only one
  pet's tasks.
- **Conflict detection** — overlapping times flagged (including two tasks at the *exact*
  same time), back-to-back tasks *not* flagged, flexible tasks never conflict.
- **Recurrence** — completing a daily task creates the next day's task, a "once" task
  does not recur, and `tasks_for_day()` returns the right tasks per weekday.
- **Plan building** — an empty task list produces an empty plan (no crash), an
  over-budget task is dropped, and a conflicting task is dropped for the higher-priority one.

- Why were these tests important?

These are the behaviors an owner actually relies on, and the edge cases (empty list, two
tasks at the same time) are exactly where scheduling code tends to break. Testing them
means I can change the code later and know immediately if I broke the core logic.

**b. Confidence**

- How confident are you that your scheduler works correctly?

**4 / 5.** All 17 tests pass and I verified the app end-to-end. I held back one star
because a few things are still simplified: weekly recurrence relies on a manually set
`weekday`, `build_plan()` treats the day as a pool of minutes rather than placing tasks on
a real clock, and preferences aren't used yet.

- What edge cases would you test next if you had more time?

Real calendar dates for weekly recurrence, a task that fits no day, tasks longer than the
whole time budget, and ordering driven by owner preferences.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The explainable plan and the way the "smarter" features layered on cleanly. Once
`fixed_time` existed, sorting by time, conflict detection, and recurrence each dropped in
without fighting the rest of the design. I'm also happy that every scheduled or dropped
task comes with a plain-English reason.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd give `build_plan()` a real timeline instead of a pool of minutes, so tasks get actual
start times and conflict detection is part of building the plan rather than a separate
check. I'd also use `Owner.preferences` to bias ordering (e.g. walks in the morning) and
put weekly recurrence on real dates.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that it is tempting to skip the struggling and learning process since it does everything for us, but it is more powerful when we understand what we are doing, and it supports us along the way.

