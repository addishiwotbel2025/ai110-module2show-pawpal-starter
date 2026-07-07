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
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
