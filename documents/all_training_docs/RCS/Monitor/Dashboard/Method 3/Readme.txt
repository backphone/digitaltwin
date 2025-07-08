SELECT 
    Final.ProblemID,
    Final.CreatedDateTime AS LastActionTime,
    CAST(DATEDIFF(SECOND, Final.CreatedDateTime, GETDATE()) / 3600.0 AS DECIMAL(10,1)) AS HoursSinceLastAction,
    GETDATE() AS SnapshotTime,
    0 AS SnapshotHour  -- Replace 5 with the current hour (e.g., 0–23)
FROM (
    SELECT
        pa.ProblemID,
        pa.CreatedDateTime,
        ROW_NUMBER() OVER (PARTITION BY pa.ProblemID ORDER BY pa.CreatedDateTime DESC) AS rn
    FROM tblProblemAction pa
    INNER JOIN (
        SELECT ProblemID
        FROM tblProblem
        WHERE AssignedToResourceID = 41       -- RCS team
          AND ProblemStatusID = 1             -- In Progress
          AND CloseDateTime IS NULL           -- Not closed
          AND ResolveDateTime IS NULL         -- Not resolved
          AND AssignedToContactID IS NULL     -- Not assigned
    ) AS ActiveRCSTickets
    ON pa.ProblemID = ActiveRCSTickets.ProblemID
) AS Final
WHERE Final.rn = 1
ORDER BY Final.CreatedDateTime ASC;





This query is what you've referred to earlier as **Method 3** — it calculates the **delay based on the last action taken** on each active ticket. Here's a breakdown of what it does:

---

## ✅ **What the query does:**

### 1. **Identifies active RCS tickets** (`ActiveRCSTickets`)

* From `tblProblem`
* Status is **In Progress** (`ProblemStatusID = 1`)
* Not **closed** or **resolved**
* Assigned to **RCS team** (`AssignedToResourceID = 41`)
* Not assigned to an individual (`AssignedToContactID IS NULL`)

---

### 2. **Finds the last action on each ticket** (`tblProblemAction`)

* Joins actions with the active tickets
* Uses `ROW_NUMBER()` to assign a rank based on **most recent action**
* Keeps **only the most recent action** per ticket (`WHERE rn = 1`)

---

### 3. **Calculates delay**

* `DATEDIFF` between `CreatedDateTime` of the **last action** and **current time**
* Converts it to **hours**, with 1 decimal place
* Adds a snapshot timestamp and a placeholder for `SnapshotHour`

---

## 🧠 **Purpose:**

> To track how long a ticket has gone **without any action** — used to monitor ticket staleness based on activity, regardless of status changes.

---

## ⚠️ Key Limitation:

* It does **not care about status** (e.g., ticket might be in "Waiting on Customer")
* It assumes all actions are meaningful (could include system-generated logs unless filtered)

---

Let me know if you'd like to integrate this logic into your current SQL canvas for comparison with Method 2.
