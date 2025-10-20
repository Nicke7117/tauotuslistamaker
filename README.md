# Automated Hypermarket Cashier Scheduler

## Table of Contents

- [Motivation](#motivation)
- [Principles of the algorithm and the scheduler](#principles-of-the-algorithm-and-the-scheduler)
- [The algorithm and the architecture](#the-algorithm-and-the-architecture)
  - [Config and Cashiers shifts](#config-and-cashiers-shifts)
  - [The TimeInterval object](#the-timeinterval-object)
  - [TimeIntervalCollection](#timeintervalcollection)
  - [ScheduleCollectionBase](#schedulecollectionbase)
  - [BaseAssignment, BreakAssignment and CheckoutAssignment](#baseassignment-breakassignment-and-checkoutassignment)
  - [Algorithm](#algorithm)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
  - [Sample Output](#sample-output)
    - [Sample cashiers.json Content](#sample-cashiersjson-content)
    - [Sample Output for the Above cashiers.json](#sample-output-for-the-above-cashiersjson)

## Motivation

After working for two years in Prisma (a grocery store), I encountered the art of making the cashier schedule for the cashiers in a big hypermarket. I immediately saw the potential to automate it to increase the efficiency of day-to-day operations, because this cashier schedule has to be made every day from scratch due to there being a different availability of cashiers day-by-day. The schedule essentially tells which checkout each cashier will be working at any moment during the day, and when each cashier will have their breaks. At first, it sounded easy, but while digging deeper, I realized that it is a complex problem after all.

My cashier schedule **program** solves all the issues; it assigns cashiers automatically to checkouts, keeps track of all the breaks, and ensures continuity and efficiency both in the aspect of keeping checkouts **continuously** open but also in the aspect of the cashiers having to change the checkout they are working at for as little as possible, all this while taking the different requirements into account like: cashiers' breaks, the ratio of tobacco checkouts open of all checkouts, **checkout** opening and closing times, and also whether a checkout is required to be open at all times.

## Principles of the algorithm and the scheduler

A reliever (or **tauottaja** in **Finnish**), is a cashier who is assigned to let cashiers in checkouts have breaks while keeping the checkout **continuously** open. What happens is that the reliever comes and replaces the cashier in the checkout to let the cashier have their scheduled break, and after the break is finished, the cashier comes back and lets the reliever continue relieving other cashiers.

Each cashier is either having their own breaks covered by themselves or a reliever. The optimal is obviously to have a reliever covering the break so the checkout operations can continue **seamlessly** and without any disturbance for the customers. Closing the checkout not only is inefficient but also causes additional costs due to the inefficiency. Still, sometimes it's necessary to have a cashier cover their own break due to too few cashiers available or if there's no other breaks needing to be covered in the near **future**. It doesn't make sense to have one cashier close their own checkout just to be able to relieve one single cashier.

There were essentially two choices for me **on** how to generate the breaks schedule and the checkouts schedule, either create the breaks schedule first and then create **the** checkouts schedule, or vice versa. Creating the checkouts list first would have been really complex due to the constraints (ratio of tobacco checkouts and checkouts required to be open). If I had created it first, it would have been really difficult to follow all the constraints because I need to ensure that all constraints are followed at all times. I decided to first assign breaks to all cashiers and with the basis of that, I could assign checkouts to cashiers and at the same time ensure that all constraints are followed.

## The algorithm and the architecture

I started this project two years ago, and finished it already once back some years ago, but the code was really bad. At some point I made it a bit more functional **in** style, but I was still not satisfied with the quality of the code; it was really messy, hard to read, and any changes would have broken it most likely. While I'm not so proud of the first versions, I am really proud of how my professional skills have developed and how this project demonstrates my development as a software engineer. This project has evolved to be a well-working application with a solid codebase that adheres **to** core OOP principles and displays my ability to model and solve a complex, real-world problem.

The project is separated into three main folders:

1. **`managers`** that contain the main "managers" of the project; the objects are `BreakManager`, `CheckoutManager`, and `DataManager`. Almost like they could be some real-world job titles assigned to employees, **although** these job titles would maybe have a **little bit** too little **responsibility**. But separating the managers into three smaller objects that have a very specific task and that contain all core logic was a good choice in my opinion.

2. **`collections`** that contain all the collections. **What do** I mean by collection in this context? Because I work a lot with time intervals, they are the core of the project, so I decided to create my own custom **data structure** for holding those time intervals. It contains `CashierScheduleCollection`, `CheckoutScheduleCollection`, `ScheduleCollectionBase`, and `TimeIntervalCollection`.

3. **`models`**, the folder that contain all the real-world entities or concepts. The `models` folder contains `AvailableInterval`, `BaseAssignment`, `BreakAssignment`, `Cashier`, `CheckoutAssignment`, `Checkout`, **and** `TimeInterval`.

Now I will explain what my thought process was behind my folders and whole architecture, and also the relations between the objects.

### Config and Cashiers shifts

There are two files that are intended to be modified by the person generating the list, if needed. One is the `config.json` file, and the other is the `cashiers.json`. `cashiers.json` is pretty straightforward; it is a list of json objects that each contain the cashier name, shift start time, and shift end time.

`config.json` contains:

1. `checkout_time_groups` where the user can assign **an** `opening_time` and a `closing_time`, `mandatory_open` (boolean) if the checkout(s) are required to stay open during their whole **shift**, and all the checkouts those rules apply for.

2. `checkouts_filling_order` that determines the filling order of the checkouts; it contains all checkouts that are NOT required to stay open. From the checkout to fill first to the one that is filled last (left to right).

3. `tobacco_checkouts` that contains the checkouts that can sell tobacco.

4. `tobacco_ratio_pool` that contains all checkouts that should be included when calculating the ratio of tobacco checkouts.

5. `tobacco_checkout_ratios` that is a list of json objects containing information about the ratios. Each object contain `max_total_checkouts` and `tobacco_checkouts`, and the objects are ordered from smallest `max_total_checkouts` to the biggest.

### The TimeInterval object

While developing the project further, the first core concept that I developed was the `TimeInterval`. Because this scheduling application relies really heavily on time intervals. In the first versions of the project, I did not even have a `TimeInterval` object; I was working with raw `datetime` objects, and I quickly realized that basically the whole project relies on time intervals and that there's a lot of duplication, and that it's so difficult to read and understand hundreds of lines with comparisons of `datetime` objects. So I created the `TimeInterval` object with multiple methods for comparing the `TimeInterval` objects with one another. But I was still not so satisfied. `TimeInterval` had a lot of unnecessary methods that were necessary for being able to compare them with **each other**. Those methods were used for example in assisting me to keep lists that contained `TimeInterval` objects sorted. To solve the problem of having `TimeIntervals` in a list, sorted and not overlapping, I created the `TimeIntervalCollection`.

### TimeIntervalCollection

The `TimeIntervalCollection` is essentially a custom **data structure** that uses **Python's** lists under the hood. It ensures that the `TimeIntervals` are always sorted and never overlap with one another. But only having a `TimeIntervalCollection` was not enough because each entity that has a schedule, like `Cashier` and `Checkout`, **needs** a `boundary_interval` for when they are available. I decided to use composition and create an abstract `ScheduleCollectionBase` class.

### ScheduleCollectionBase

The `ScheduleCollectionBase` is an abstract class that has a `TimeIntervalCollection` and also additional instance variables like `boundary_interval` and `_availability`. It essentially acts as the man-in-the-middle that receives orders from the owner entity (`Cashier` or `Checkout`) and delegates some tasks to the `TimeIntervalCollection` while also using the additional information the instance variables `boundary_interval` **and** `_availability` provide. While in theory I think I could have extended the `TimeIntervalCollection`, it felt more natural for me for entities to have a schedule and the schedule having a `TimeIntervalCollection` for storing the `TimeIntervals`. Also because of past experiences, I think that composition was better than inheritance in this case.

### BaseAssignment, BreakAssignment and CheckoutAssignment

I had an issue with modeling the events that represent some kind of `TimeInterval`, because I wanted all of the schedules to reference the same object if they were the same thing essentially. Let's say a break of a cashier; **it** sounds simple, but the break can have a reliever or not, so I had to figure out how I will model such a simple thing, that maybe wasn't so simple after all. I wanted the break to be the same object in the checkout, **the** cashier (whose break it is), and the reliever. I could have had multiple objects (`RelieverAssignment`, `CheckoutAssignment` (that already exists for normal assignments), and `CashierBreakAssignment`) representing the same break; my architecture or logic did not prevent it, but I thought that maybe it's the best to still not do it to prevent any bugs or corrupted data from happening, because those bugs could be pretty tricky to solve. Also I know that with one object representing a break, it could be beneficial in the future if I would want to change the logic and be able to move breaks after they have been assigned already to cashiers, checkouts, and relievers. This kind of thinking is obviously against YAGNI (You aren't **going to** need it), but taking overall good practices into account and the risk of data being corrupted, I decided to solve it by having only one **object**, and I don't think it's either semantically wrong.

Then I created `CheckoutAssignment`, that was pretty obvious and straightforward for me.

Because both of these objects are assignments that have a cashier who is the "main character" of the object and also **a** checkout, I thought it makes very much sense to have an abstract base class `BaseAssignment` that inherits from `TimeInterval` because these are some sort of `TimeIntervals`.

### Algorithm

As I already said earlier, first, I assign everyone their breaks and the times of the breaks. First, obviously while processing the `cashiers.json` data, I determine how many breaks each cashier gets based on the length of their shift, and then I calculate the ideal start and end times of the breaks by spreading all breaks evenly throughout their shift. After assigning all cashiers ideal break times, my `BreakManager` kicks in. **Its** job is now to create the breaks list or **tauotuslista** as it is in **Finnish**. So basically determining the best possible schedule for breaks by assigning relievers or having cashiers have breaks on their own.

I am using a greedy heuristic algorithm utilizing **a** weighted score to find the best **tauottajas**. To make the breaks flexible, I allowed them to move by maximum **of** 30 minutes (forward or backwards); this way they will fit **seamlessly** after one another. I sort all unassigned breaks chronologically and for each cashier I try to find the one who can cover the most, or more accurately, the one who gets the most points by my heuristic, and I continue looping until there are no breaks left to assign. So I start and try to always assign the break that has been moved $-30$ min backwards to the current selected cashier. If it doesn't fit, then I move to $-15$ min, etc., until $+30$ min. If it fits at some point in the selected **cashier's** schedule, I assign it there. By always testing $-30$, $-15$, $0$, $+15$, $+30$ min, I ensure that the breaks will fit well even if some cashiers' breaks are overlapping a **little bit**. Let's say Cashier X has a lunch break at 11:00-11:30, and Cashier Y a normal break at 11:15-11:30. You see they don't fit, but by moving Cashier **Y's** break $+15$ min, they fit **seamlessly**. I also had an issue of there being too few breaks assigned to a reliever, **because** it doesn't make too much sense to have a dedicated reliever to relieve just two single breaks that are not consecutive.

To solve the problem of there being too many breaks left out in times without many cashiers, I implemented the weighted score. The weighted score gives points: 1. if a break is consecutive with another break, 2. if a break ends before 11, and 3. if a break ends after 20. With the implementation of this heuristic and a minimum score requirement, I was able to prevent a reliever having only a very few coverages, but still to encourage the cashier to be a reliever if the breaks to relieve are consecutive and there's not many cashiers working. This is smart because when there **are** fewer cashiers and checkouts open **they** have a bigger impact compared to when **there are** many customers. It can also be more difficult to close a checkout to have a break because there might be a sudden rush of customers. Also the consecutive breaks bonus obviously favors the more efficient cashier of **the** cashiers who have a long shift and are able to handle very many **relieving duties**. So in that case also the most efficient cashier is chosen to be the reliever. If the minimum required score of the heuristic is not achieved for any cashier that includes a break **(x)**, then it is assigned no reliever and the cashier has to go to the break on their own.

The `CheckoutManager` is responsible for the crucial task of assigning available cashiers to open checkouts in real-time, minute by minute. Unlike the `BreakManager`, which uses a single Greedy Heuristic to find a global optimum for the whole break list, the `CheckoutManager` uses an event simulation logic based on **15-minute** time slices and a multi-tiered Priority Pipelining logic to make local, immediate assignment decisions. What the algorithm does is that it sees a time window of **15 minutes** and assigns cashiers; it does it from **the** start until the last checkout is closed. The advantages are clear, because it is difficult to assign a cashier to a specific checkout for a long interval without knowing which other checkouts will be open, due to the need of following all config constraints. So I decided that it's the easiest to think of it as a puzzle to glue together and advance **in 15-minute** intervals at a time.

By assigning cashiers to checkouts **in 15-minute** intervals at a time, I am able to determine easily which cashiers are working or available to work (e.g., either completely free cashiers or a cashier who is on their reliever duty). This way I know how many checkouts will be open, and I will also be able to determine whether there's enough cashiers to also attend the checkouts that are required to be open. After prioritizing the mandatory checkouts, I favor keeping the already open checkouts to stay open, to favor smooth and efficient transitions, efficiency, and **a** great customer experience by preventing unnecessarily opening or closing lanes. After those checkouts are chosen to be attended, if there's still checkouts to be selected to **be** attended, I fill lanes according to the predefined `checkout_filling_order` in **the** config. After **deciding** all checkouts that will be attended, I do tobacco ratio balancing. The algorithm applies a ratio optimization loop to ensure that within the designated tobacco-selling checkouts, the correct minimum number of lanes is open. If the current selection fails the ratio requirement, the algorithm will swap a lower-priority, non-tobacco checkout with an available tobacco checkout, guaranteeing compliance.

Once all checkouts to be filled are chosen, the algorithm assigns cashiers to those checkouts. The algorithm first attempts to extend the assignment of the cashier who was at that specific checkout in the previous time interval, preserving flow and continuity. If the previous cashier is now due for a break, the system automatically assigns their designated reliever to the checkout, guaranteeing the continuity of service. Only after prioritizing continuity and scheduled breaks does the system look to assign any remaining available cashiers to the remaining open checkouts, creating new `CheckoutAssignment` intervals.

This algorithm maximizes **efficiency** in **the** breaks schedule and also maximizes operational efficiency and customer-friendly checkout assignments.

## Getting Started

### Prerequisites

- **Python 3.10** or later
- No external dependencies required (uses only Python standard library)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nicke7117/tauotuslistamaker.git
   cd tauotuslistamaker
   ```

2. **Verify Python installation:**
   ```bash
   py --version
   # Should show Python 3.10 or later
   ```

### Configuration

The application uses two JSON configuration files:

1. **`cashiers.json`** - Contains cashier information:
   ```json
   [
     {
       "name": "John Doe",
       "shift_start": "08:00",
       "shift_end": "16:00"
     }
   ]
   ```

2. **`config.json`** - Contains checkout configuration and rules (see detailed explanation below)

Modify these files according to your store's requirements before running the scheduler.

### Running the Application

Execute the scheduler from the project root:

```bash
py -m tauotuslistamaker.main
```

The application will:
1. Load cashier data from `cashiers.json`
2. Load configuration from `config.json`
3. Generate break assignments using the greedy algorithm
4. Assign cashiers to checkouts in 15-minute intervals
5. Display the complete schedule with breaks and checkout assignments

### Sample Output

The program generates three main sections:
- **Breaks List Schedule**: Shows which cashiers are assigned as relievers (tauottajas) and which breaks they cover
- **All Cashiers' Personal Schedules**: Individual schedules for each cashier showing their breaks and checkout assignments
- **Checkout Assignment Schedule**: Shows which cashiers are assigned to each checkout over time

#### Sample cashiers.json Content

```json
[
    {
        "name": "Riley Rivera",
        "shift_start": "11:00",
        "shift_end": "19:15"
    },
    {
        "name": "Hunter Wilson",
        "shift_start": "08:00",
        "shift_end": "16:00"
    },
    {
        "name": "Avery Martin",
        "shift_start": "16:00",
        "shift_end": "00:00"
    },
    {
        "name": "Tanner Garcia",
        "shift_start": "10:30",
        "shift_end": "18:15"
    },
    {
        "name": "Harper Hill",
        "shift_start": "17:15",
        "shift_end": "21:15"
    },
    {
        "name": "Taylor Moore",
        "shift_start": "09:00",
        "shift_end": "17:15"
    },
    {
        "name": "Dana Johnson",
        "shift_start": "06:00",
        "shift_end": "14:00"
    },
    {
        "name": "Noah Martin",
        "shift_start": "09:30",
        "shift_end": "16:30"
    },
    {
        "name": "Hunter Taylor",
        "shift_start": "14:00",
        "shift_end": "22:00"            
    },
    {
        "name": "Sage Adams",
        "shift_start": "10:00",
        "shift_end": "17:30"            
    },
    {
        "name": "Drew Ramirez",
        "shift_start": "12:00",
        "shift_end": "20:00"            
    },
    {
        "name": "Quinn Brown",
        "shift_start": "12:45",
        "shift_end": "17:30"            
    },
    {
        "name": "Riley Thompson",
        "shift_start": "18:15",
        "shift_end": "00:15"            
    },
    {
        "name": "Ellis Garcia",
        "shift_start": "07:30",
        "shift_end": "15:30"            
    },
    {
        "name": "Taylor Garcia",
        "shift_start": "15:30",
        "shift_end": "23:30"            
    }
]
```

#### Sample Output for the Above cashiers.json

```
--- Breaks List Schedule ---
Tauottaja 1: Riley Rivera (total_minutes=690.0)
  - covers: Taylor Moore | 1900-01-01 11:00:00 -> 1900-01-01 11:15:00
  - covers: Noah Martin | 1900-01-01 11:15:00 -> 1900-01-01 11:30:00
  - covers: Ellis Garcia | 1900-01-01 11:30:00 -> 1900-01-01 12:00:00
  - covers: Sage Adams | 1900-01-01 12:00:00 -> 1900-01-01 12:15:00
  - covers: Hunter Wilson | 1900-01-01 12:15:00 -> 1900-01-01 12:45:00
  - covers: Tanner Garcia | 1900-01-01 12:45:00 -> 1900-01-01 13:00:00
  - covers: Dana Johnson | 1900-01-01 13:15:00 -> 1900-01-01 13:30:00
  - covers: Taylor Moore | 1900-01-01 13:30:00 -> 1900-01-01 14:00:00
  - covers: Sage Adams | 1900-01-01 14:00:00 -> 1900-01-01 14:30:00
  - covers: Drew Ramirez | 1900-01-01 14:30:00 -> 1900-01-01 14:45:00
  - covers: Noah Martin | 1900-01-01 14:45:00 -> 1900-01-01 15:00:00
  - covers: Hunter Wilson | 1900-01-01 15:00:00 -> 1900-01-01 15:15:00
  - covers: Taylor Moore | 1900-01-01 15:45:00 -> 1900-01-01 16:00:00
  - covers: Hunter Taylor | 1900-01-01 16:00:00 -> 1900-01-01 16:15:00
  - covers: Drew Ramirez | 1900-01-01 16:15:00 -> 1900-01-01 16:45:00
  - covers: Sage Adams | 1900-01-01 16:45:00 -> 1900-01-01 17:00:00
  - covers: Tanner Garcia | 1900-01-01 17:00:00 -> 1900-01-01 17:15:00
  - covers: Taylor Garcia | 1900-01-01 17:15:00 -> 1900-01-01 17:30:00
  - covers: Avery Martin | 1900-01-01 17:30:00 -> 1900-01-01 17:45:00
  - covers: Hunter Taylor | 1900-01-01 18:00:00 -> 1900-01-01 18:30:00
  - covers: Drew Ramirez | 1900-01-01 18:30:00 -> 1900-01-01 18:45:00
  - covers: Harper Hill | 1900-01-01 18:45:00 -> 1900-01-01 19:00:00
Tauottaja 2: Hunter Taylor (total_minutes=225.0)
  - covers: Ellis Garcia | 1900-01-01 14:00:00 -> 1900-01-01 14:15:00
  - covers: Tanner Garcia | 1900-01-01 14:15:00 -> 1900-01-01 14:45:00
  - covers: Quinn Brown | 1900-01-01 14:45:00 -> 1900-01-01 15:00:00
  - covers: Taylor Garcia | 1900-01-01 19:15:00 -> 1900-01-01 19:45:00
  - covers: Avery Martin | 1900-01-01 19:45:00 -> 1900-01-01 20:15:00
  - covers: Riley Thompson | 1900-01-01 20:15:00 -> 1900-01-01 20:30:00
  - covers: Taylor Garcia | 1900-01-01 21:45:00 -> 1900-01-01 22:00:00
Tauottaja 3: Noah Martin (total_minutes=112.5)
  - covers: Ellis Garcia | 1900-01-01 09:30:00 -> 1900-01-01 09:45:00
  - covers: Hunter Wilson | 1900-01-01 09:45:00 -> 1900-01-01 10:00:00
  - covers: Dana Johnson | 1900-01-01 10:00:00 -> 1900-01-01 10:30:00
Tauottaja 4: Taylor Garcia (total_minutes=60.0)
  - covers: Riley Thompson | 1900-01-01 22:00:00 -> 1900-01-01 22:15:00
  - covers: Avery Martin | 1900-01-01 22:15:00 -> 1900-01-01 22:30:00
Tauottaja 5: None (total_minutes=15.0)
  - covers: Dana Johnson | 1900-01-01 08:00:00 -> 1900-01-01 08:15:00


--- All Cashiers' Personal Schedules ---

CASHIER: Riley Rivera
----------------------------------------
   Schedule:
     1. 11:00-11:15 (15 min) - Break Coverage (for Taylor Moore)
     2. 11:15-11:30 (15 min) - Break Coverage (for Noah Martin)
     3. 11:30-12:00 (30 min) - Break Coverage (for Ellis Garcia)
     4. 12:00-12:15 (15 min) - Break Coverage (for Sage Adams)
     5. 12:15-12:45 (30 min) - Break Coverage (for Hunter Wilson)
     6. 12:45-13:00 (15 min) - Break Coverage (for Tanner Garcia)
     7. 13:00-13:15 (15 min) - Own Break (self-covered)
     8. 13:15-13:30 (15 min) - Break Coverage (for Dana Johnson)
     9. 13:30-14:00 (30 min) - Break Coverage (for Taylor Moore)
     10. 14:00-14:30 (30 min) - Break Coverage (for Sage Adams)
     11. 14:30-14:45 (15 min) - Break Coverage (for Drew Ramirez)
     12. 14:45-15:00 (15 min) - Break Coverage (for Noah Martin)
     13. 15:00-15:15 (15 min) - Break Coverage (for Hunter Wilson)
     14. 15:15-15:45 (30 min) - Own Break (self-covered)
     15. 15:45-16:00 (15 min) - Break Coverage (for Taylor Moore)
     16. 16:00-16:15 (15 min) - Break Coverage (for Hunter Taylor)
     17. 16:15-16:45 (30 min) - Break Coverage (for Drew Ramirez)
     18. 16:45-17:00 (15 min) - Break Coverage (for Sage Adams)
     19. 17:00-17:15 (15 min) - Break Coverage (for Tanner Garcia)
     20. 17:15-17:30 (15 min) - Break Coverage (for Taylor Garcia)
     21. 17:30-17:45 (15 min) - Break Coverage (for Avery Martin)
     22. 17:45-18:00 (15 min) - Own Break (self-covered)
     23. 18:00-18:30 (30 min) - Break Coverage (for Hunter Taylor)
     24. 18:30-18:45 (15 min) - Break Coverage (for Drew Ramirez)
     25. 18:45-19:00 (15 min) - Break Coverage (for Harper Hill)
     26. 19:00-19:15 (15 min) - Checkout

CASHIER: Hunter Wilson
----------------------------------------
   Schedule:
     1. 08:00-09:45 (105 min) - Checkout
     2. 09:45-10:00 (15 min) - Own Break (covered by Noah Martin)
     3. 10:00-12:15 (135 min) - Checkout
     4. 12:15-12:45 (30 min) - Own Break (covered by Riley Rivera)
     5. 12:45-15:00 (135 min) - Checkout
     6. 15:00-15:15 (15 min) - Own Break (covered by Riley Rivera)
     7. 15:15-16:00 (45 min) - Checkout

CASHIER: Avery Martin
----------------------------------------
   Schedule:
     1. 16:00-16:30 (30 min) - Checkout
     2. 16:30-17:30 (60 min) - Checkout
     3. 17:30-17:45 (15 min) - Own Break (covered by Riley Rivera)
     4. 17:45-19:45 (120 min) - Checkout
     5. 19:45-20:15 (30 min) - Own Break (covered by Hunter Taylor)
     6. 20:15-22:15 (120 min) - Checkout
     7. 22:15-22:30 (15 min) - Own Break (covered by Taylor Garcia)
     8. 22:30-00:00 (90 min) - Checkout

CASHIER: Tanner Garcia
----------------------------------------
   Schedule:
     1. 10:30-12:45 (135 min) - Checkout
     2. 12:45-13:00 (15 min) - Own Break (covered by Riley Rivera)
     3. 13:00-14:15 (75 min) - Checkout
     4. 14:15-14:45 (30 min) - Own Break (covered by Hunter Taylor)
     5. 14:45-17:00 (135 min) - Checkout
     6. 17:00-17:15 (15 min) - Own Break (covered by Riley Rivera)
     7. 17:15-18:15 (60 min) - Checkout

CASHIER: Harper Hill
----------------------------------------
   Schedule:
     1. 17:15-18:45 (90 min) - Checkout
     2. 18:45-19:00 (15 min) - Own Break (covered by Riley Rivera)
     3. 19:00-21:00 (120 min) - Checkout
     4. 21:00-21:15 (15 min) - Checkout

CASHIER: Taylor Moore
----------------------------------------
   Schedule:
     1. 09:00-11:00 (120 min) - Checkout
     2. 11:00-11:15 (15 min) - Own Break (covered by Riley Rivera)
     3. 11:15-13:30 (135 min) - Checkout
     4. 13:30-14:00 (30 min) - Own Break (covered by Riley Rivera)
     5. 14:00-15:45 (105 min) - Checkout
     6. 15:45-16:00 (15 min) - Own Break (covered by Riley Rivera)
     7. 16:00-17:15 (75 min) - Checkout

CASHIER: Dana Johnson
----------------------------------------
   Schedule:
     1. 06:00-08:00 (120 min) - Checkout
     2. 08:00-08:15 (15 min) - Own Break (self-covered)
     3. 08:15-09:00 (45 min) - Checkout
     4. 09:00-10:00 (60 min) - Checkout
     5. 10:00-10:30 (30 min) - Own Break (covered by Noah Martin)
     6. 10:30-13:15 (165 min) - Checkout
     7. 13:15-13:30 (15 min) - Own Break (covered by Riley Rivera)
     8. 13:30-14:00 (30 min) - Checkout

CASHIER: Noah Martin
----------------------------------------
   Schedule:
     1. 09:30-09:45 (15 min) - Break Coverage (for Ellis Garcia)
     2. 09:45-10:00 (15 min) - Break Coverage (for Hunter Wilson)
     3. 10:00-10:30 (30 min) - Break Coverage (for Dana Johnson)
     4. 10:30-11:15 (45 min) - Checkout
     5. 11:15-11:30 (15 min) - Own Break (covered by Riley Rivera)
     6. 11:30-14:45 (195 min) - Checkout
     7. 14:45-15:00 (15 min) - Own Break (covered by Riley Rivera)
     8. 15:00-16:30 (90 min) - Checkout

CASHIER: Hunter Taylor
----------------------------------------
   Schedule:
     1. 14:00-14:15 (15 min) - Break Coverage (for Ellis Garcia)
     2. 14:15-14:45 (30 min) - Break Coverage (for Tanner Garcia)
     3. 14:45-15:00 (15 min) - Break Coverage (for Quinn Brown)
     4. 15:00-16:00 (60 min) - Checkout
     5. 16:00-16:15 (15 min) - Own Break (covered by Riley Rivera)
     6. 16:15-17:30 (75 min) - Checkout
     7. 17:30-18:00 (30 min) - Checkout
     8. 18:00-18:30 (30 min) - Own Break (covered by Riley Rivera)
     9. 18:30-19:15 (45 min) - Checkout
     10. 19:15-19:45 (30 min) - Break Coverage (for Taylor Garcia)
     11. 19:45-20:15 (30 min) - Break Coverage (for Avery Martin)
     12. 20:15-20:30 (15 min) - Break Coverage (for Riley Thompson)
     13. 20:30-20:45 (15 min) - Checkout
     14. 20:45-21:00 (15 min) - Own Break (self-covered)
     15. 21:00-21:45 (45 min) - Checkout
     16. 21:45-22:00 (15 min) - Break Coverage (for Taylor Garcia)

CASHIER: Sage Adams
----------------------------------------
   Schedule:
     1. 10:00-12:00 (120 min) - Checkout
     2. 12:00-12:15 (15 min) - Own Break (covered by Riley Rivera)
     3. 12:15-14:00 (105 min) - Checkout
     4. 14:00-14:30 (30 min) - Own Break (covered by Riley Rivera)
     5. 14:30-16:45 (135 min) - Checkout
     6. 16:45-17:00 (15 min) - Own Break (covered by Riley Rivera)
     7. 17:00-17:30 (30 min) - Checkout

CASHIER: Drew Ramirez
----------------------------------------
   Schedule:
     1. 12:00-14:30 (150 min) - Checkout
     2. 14:30-14:45 (15 min) - Own Break (covered by Riley Rivera)
     3. 14:45-16:15 (90 min) - Checkout
     4. 16:15-16:45 (30 min) - Own Break (covered by Riley Rivera)
     5. 16:45-18:30 (105 min) - Checkout
     6. 18:30-18:45 (15 min) - Own Break (covered by Riley Rivera)
     7. 18:45-20:00 (75 min) - Checkout

CASHIER: Quinn Brown
----------------------------------------
   Schedule:
     1. 12:45-14:00 (75 min) - Checkout
     2. 14:00-14:45 (45 min) - Checkout
     3. 14:45-15:00 (15 min) - Own Break (covered by Hunter Taylor)
     4. 15:00-17:30 (150 min) - Checkout

CASHIER: Riley Thompson
----------------------------------------
   Schedule:
     1. 18:15-19:15 (60 min) - Checkout
     2. 19:15-20:15 (60 min) - Checkout
     3. 20:15-20:30 (15 min) - Own Break (covered by Hunter Taylor)
     4. 20:30-21:00 (30 min) - Checkout
     5. 21:00-21:15 (15 min) - Checkout
     6. 21:15-21:45 (30 min) - Checkout
     7. 21:45-22:00 (15 min) - Checkout
     8. 22:00-22:15 (15 min) - Own Break (covered by Taylor Garcia)
     9. 22:15-00:00 (105 min) - Checkout

CASHIER: Ellis Garcia
----------------------------------------
   Schedule:
     1. 07:30-09:30 (120 min) - Checkout
     2. 09:30-09:45 (15 min) - Own Break (covered by Noah Martin)
     3. 09:45-11:30 (105 min) - Checkout
     4. 11:30-12:00 (30 min) - Own Break (covered by Riley Rivera)
     5. 12:00-14:00 (120 min) - Checkout
     6. 14:00-14:15 (15 min) - Own Break (covered by Hunter Taylor)
     7. 14:15-15:30 (75 min) - Checkout

CASHIER: Taylor Garcia
----------------------------------------
   Schedule:
     1. 15:30-17:15 (105 min) - Checkout
     2. 17:15-17:30 (15 min) - Own Break (covered by Riley Rivera)
     3. 17:30-19:15 (105 min) - Checkout
     4. 19:15-19:45 (30 min) - Own Break (covered by Hunter Taylor)
     5. 19:45-20:00 (15 min) - Checkout
     6. 20:00-21:45 (105 min) - Checkout
     7. 21:45-22:00 (15 min) - Own Break (covered by Hunter Taylor)
     8. 22:00-22:15 (15 min) - Break Coverage (for Riley Thompson)
     9. 22:15-22:30 (15 min) - Break Coverage (for Avery Martin)
     10. 22:30-23:30 (60 min) - Checkout

--- End of Cashiers' Schedules ---


--- Checkout Assignment Schedule ---

CHECKOUT 15
   Type: Tobacco Checkout
   Status: Optional
----------------------------------------
   Assignments:
     06:00-08:00 (120 min) - Dana Johnson (Checkout)
     08:00-09:45 (105 min) - Hunter Wilson (Checkout)
     09:45-10:00 (15 min) - Hunter Wilson (Break)
       Tauottaja: Noah Martin
     10:00-12:15 (135 min) - Hunter Wilson (Checkout)
     12:15-12:45 (30 min) - Hunter Wilson (Break)
       Tauottaja: Riley Rivera
     12:45-15:00 (135 min) - Hunter Wilson (Checkout)
     15:00-15:15 (15 min) - Hunter Wilson (Break)
       Tauottaja: Riley Rivera
     15:15-16:00 (45 min) - Hunter Wilson (Checkout)
     16:00-16:30 (30 min) - Avery Martin (Checkout)
     17:45-19:45 (120 min) - Avery Martin (Checkout)
     19:45-20:15 (30 min) - Avery Martin (Break)
       Tauottaja: Hunter Taylor
     20:15-22:15 (120 min) - Avery Martin (Checkout)
     22:15-22:30 (15 min) - Avery Martin (Break)
       Tauottaja: Taylor Garcia
     22:30-00:00 (90 min) - Avery Martin (Checkout)

CHECKOUT 14
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   Assignments:
     10:30-12:45 (135 min) - Tanner Garcia (Checkout)
     12:45-13:00 (15 min) - Tanner Garcia (Break)
       Tauottaja: Riley Rivera
     13:00-14:15 (75 min) - Tanner Garcia (Checkout)
     14:15-14:45 (30 min) - Tanner Garcia (Break)
       Tauottaja: Hunter Taylor
     14:45-17:00 (135 min) - Tanner Garcia (Checkout)
     17:00-17:15 (15 min) - Tanner Garcia (Break)
       Tauottaja: Riley Rivera
     17:15-18:15 (60 min) - Tanner Garcia (Checkout)
     18:15-19:15 (60 min) - Riley Thompson (Checkout)
     21:00-21:15 (15 min) - Riley Thompson (Checkout)

CHECKOUT 13
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   Assignments:
     10:30-11:15 (45 min) - Noah Martin (Checkout)
     11:15-11:30 (15 min) - Noah Martin (Break)
       Tauottaja: Riley Rivera
     11:30-14:45 (195 min) - Noah Martin (Checkout)
     14:45-15:00 (15 min) - Noah Martin (Break)
       Tauottaja: Riley Rivera
     15:00-16:30 (90 min) - Noah Martin (Checkout)
     16:30-17:30 (60 min) - Avery Martin (Checkout)

CHECKOUT 12
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   Assignments:
     12:00-14:30 (150 min) - Drew Ramirez (Checkout)
     14:30-14:45 (15 min) - Drew Ramirez (Break)
       Tauottaja: Riley Rivera
     14:45-16:15 (90 min) - Drew Ramirez (Checkout)
     16:15-16:45 (30 min) - Drew Ramirez (Break)
       Tauottaja: Riley Rivera
     16:45-18:30 (105 min) - Drew Ramirez (Checkout)
     18:30-18:45 (15 min) - Drew Ramirez (Break)
       Tauottaja: Riley Rivera
     18:45-20:00 (75 min) - Drew Ramirez (Checkout)
     20:00-21:45 (105 min) - Taylor Garcia (Checkout)
     21:45-22:00 (15 min) - Taylor Garcia (Break)
       Tauottaja: Hunter Taylor

CHECKOUT 11
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   Assignments:
     12:45-14:00 (75 min) - Quinn Brown (Checkout)
     15:00-16:00 (60 min) - Hunter Taylor (Checkout)
     16:00-16:15 (15 min) - Hunter Taylor (Break)
       Tauottaja: Riley Rivera
     16:15-17:30 (75 min) - Hunter Taylor (Checkout)

CHECKOUT 10
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   No assignments

CHECKOUT 9
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   No assignments

CHECKOUT 8
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   No assignments

CHECKOUT 7
   Type: Tobacco Checkout
   Status: Optional
----------------------------------------
   Assignments:
     07:30-09:30 (120 min) - Ellis Garcia (Checkout)
     09:30-09:45 (15 min) - Ellis Garcia (Break)
       Tauottaja: Noah Martin
     09:45-11:30 (105 min) - Ellis Garcia (Checkout)
     11:30-12:00 (30 min) - Ellis Garcia (Break)
       Tauottaja: Riley Rivera
     12:00-14:00 (120 min) - Ellis Garcia (Checkout)
     14:00-14:15 (15 min) - Ellis Garcia (Break)
       Tauottaja: Hunter Taylor
     14:15-15:30 (75 min) - Ellis Garcia (Checkout)
     15:30-17:15 (105 min) - Taylor Garcia (Checkout)
     17:15-17:30 (15 min) - Taylor Garcia (Break)
       Tauottaja: Riley Rivera
     17:30-19:15 (105 min) - Taylor Garcia (Checkout)
     19:15-19:45 (30 min) - Taylor Garcia (Break)
       Tauottaja: Hunter Taylor
     19:45-20:00 (15 min) - Taylor Garcia (Checkout)
     20:30-20:45 (15 min) - Hunter Taylor (Checkout)
     21:00-21:15 (15 min) - Harper Hill (Checkout)
     21:15-21:45 (30 min) - Riley Thompson (Checkout)
     22:15-00:00 (105 min) - Riley Thompson (Checkout)

CHECKOUT 6
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   No assignments

CHECKOUT 5
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   No assignments

CHECKOUT 4
   Type: Tobacco Checkout
   Status: Optional
----------------------------------------
   Assignments:
     08:15-09:00 (45 min) - Dana Johnson (Checkout)
     10:00-12:00 (120 min) - Sage Adams (Checkout)
     12:00-12:15 (15 min) - Sage Adams (Break)
       Tauottaja: Riley Rivera
     12:15-14:00 (105 min) - Sage Adams (Checkout)
     14:00-14:30 (30 min) - Sage Adams (Break)
       Tauottaja: Riley Rivera
     14:30-16:45 (135 min) - Sage Adams (Checkout)
     16:45-17:00 (15 min) - Sage Adams (Break)
       Tauottaja: Riley Rivera
     17:00-17:30 (30 min) - Sage Adams (Checkout)
     19:00-19:15 (15 min) - Riley Rivera (Checkout)
     21:00-21:45 (45 min) - Hunter Taylor (Checkout)
     21:45-22:00 (15 min) - Riley Thompson (Checkout)
     22:30-23:30 (60 min) - Taylor Garcia (Checkout)

CHECKOUT 3
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   No assignments

CHECKOUT 2
   Type: Regular Checkout
   Status: Optional
----------------------------------------
   No assignments

CHECKOUT 1
   Type: Regular Checkout
   Status: Mandatory Open
----------------------------------------
   Assignments:
     09:00-11:00 (120 min) - Taylor Moore (Checkout)
     11:00-11:15 (15 min) - Taylor Moore (Break)
       Tauottaja: Riley Rivera
     11:15-13:30 (135 min) - Taylor Moore (Checkout)
     13:30-14:00 (30 min) - Taylor Moore (Break)
       Tauottaja: Riley Rivera
     14:00-15:45 (105 min) - Taylor Moore (Checkout)
     15:45-16:00 (15 min) - Taylor Moore (Break)
       Tauottaja: Riley Rivera
     16:00-17:15 (75 min) - Taylor Moore (Checkout)
     17:15-18:45 (90 min) - Harper Hill (Checkout)
     18:45-19:00 (15 min) - Harper Hill (Break)
       Tauottaja: Riley Rivera
     19:00-21:00 (120 min) - Harper Hill (Checkout)

CHECKOUT Self Service 1
   Type: Regular Checkout
   Status: Mandatory Open
----------------------------------------
   Assignments:
     09:00-10:00 (60 min) - Dana Johnson (Checkout)
     10:00-10:30 (30 min) - Dana Johnson (Break)
       Tauottaja: Noah Martin
     10:30-13:15 (165 min) - Dana Johnson (Checkout)
     13:15-13:30 (15 min) - Dana Johnson (Break)
       Tauottaja: Riley Rivera
     13:30-14:00 (30 min) - Dana Johnson (Checkout)
     14:00-14:45 (45 min) - Quinn Brown (Checkout)
     14:45-15:00 (15 min) - Quinn Brown (Break)
       Tauottaja: Hunter Taylor
     15:00-17:30 (150 min) - Quinn Brown (Checkout)
     17:30-18:00 (30 min) - Hunter Taylor (Checkout)
     18:00-18:30 (30 min) - Hunter Taylor (Break)
       Tauottaja: Riley Rivera
     18:30-19:15 (45 min) - Hunter Taylor (Checkout)
     19:15-20:15 (60 min) - Riley Thompson (Checkout)
     20:15-20:30 (15 min) - Riley Thompson (Break)
       Tauottaja: Hunter Taylor
     20:30-21:00 (30 min) - Riley Thompson (Checkout)

CHECKOUT Self Service 2
   Type: Regular Checkout
   Status: Mandatory Open
----------------------------------------
   Assignments:
     09:00-10:00 (60 min) - Dana Johnson (Checkout)
     10:00-10:30 (30 min) - Dana Johnson (Break)
       Tauottaja: Noah Martin
     10:30-13:15 (165 min) - Dana Johnson (Checkout)
     13:15-13:30 (15 min) - Dana Johnson (Break)
       Tauottaja: Riley Rivera
     13:30-14:00 (30 min) - Dana Johnson (Checkout)
     14:00-14:45 (45 min) - Quinn Brown (Checkout)
     14:45-15:00 (15 min) - Quinn Brown (Break)
       Tauottaja: Hunter Taylor
     15:00-17:30 (150 min) - Quinn Brown (Checkout)
     17:30-18:00 (30 min) - Hunter Taylor (Checkout)
     18:00-18:30 (30 min) - Hunter Taylor (Break)
       Tauottaja: Riley Rivera
     18:30-19:15 (45 min) - Hunter Taylor (Checkout)
     19:15-20:15 (60 min) - Riley Thompson (Checkout)
     20:15-20:30 (15 min) - Riley Thompson (Break)
       Tauottaja: Hunter Taylor
     20:30-21:00 (30 min) - Riley Thompson (Checkout)

--- End of Checkout Assignment Schedule ---
```