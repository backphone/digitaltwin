-- NOTE: This query calculates how long a ticket has remained continuously in 'In Progress' status.
-- It assumes that tblProblemChangeLog reliably logs all status changes.
-- However, if a ticket's status is changed (e.g., to 'Waiting on Customer') but not recorded in the changelog,
-- the algorithm may mistakenly assume the ticket is still in progress since the last 'In Progress' event.
-- This may cause some tickets that are actually in 'In Progress' to be excluded from the result if the changelog is incomplete. 
-- Simplified logic: we rely on tblProblem to identify currently active 'In Progress' tickets, and we check the latest log to ensure alignment.
-- If the last ticket changelog entry shows that the ticket was 'In Progress' but closed, the ticket is disregarded, since the "in progress" time is then not accurate

-- KNOWN EXCEPTIONS / EDGE CASES TO CONSIDER (METHOD 2 & METHOD 3):
-- - Some status changes may not be captured in tblProblemChangeLog
-- - Tickets that were previously resolved but re-entered 'In Progress' may not be flagged accurately - disregarded now as mentioned above
-- - Incoming emails may not originate from the actual customer (e.g., internal escalations or monitoring bots)
-- - A ticket may appear unresolved in tblProblem, but the status change log does not reflect the full state history
-- - Delays based on last action (Method 3) may be skewed by automated or non-customer actions (e.g., internal notes), or 2nd email from customer
-- - Method 2 may miss valid In Progress states if the most recent status update wasn’t captured or synced properly
-- - Method 2: Tickets reassigned between queues may not be reflected unless `AssignedToResourceID` tracking is precise

WITH ActiveRCSTickets AS (
    SELECT ProblemID
    FROM tblProblem
    WHERE 
        ProblemStatusID = 1               -- Still in progress
        AND CaseClosed = 0                -- Not closed
        AND ResolvedBy IS NULL            -- Not resolved
        AND AssignedToResourceID = 41     -- RCS only
        AND AssignedToContactID IS NULL   -- Not individually assigned
),

-- Get all status change logs for those tickets
TicketLogs AS (
    SELECT 
        pcl.ProblemID, 
        pcl.ModifiedDateTime,
        pcl.ProblemStatusID,
        pcl.CaseClosed
    FROM tblProblemChangeLog pcl
    INNER JOIN ActiveRCSTickets ar ON pcl.ProblemID = ar.ProblemID
),

-- Identify the latest log per ticket
LatestLog AS (
    SELECT 
        ProblemID, 
        MAX(ModifiedDateTime) AS LastStatusTime
    FROM TicketLogs
    GROUP BY ProblemID
),

-- Ensure the last log confirms the status is still In Progress AND not closed
ValidStatus AS (
    SELECT tl.ProblemID, tl.ModifiedDateTime AS LastInProgressTime
    FROM TicketLogs tl
    INNER JOIN LatestLog l 
        ON tl.ProblemID = l.ProblemID AND tl.ModifiedDateTime = l.LastStatusTime
    WHERE 
        tl.ProblemStatusID = 1
        AND ISNULL(CAST(tl.CaseClosed AS VARCHAR), '0') = '0'  -- explicitly confirm not closed
)

-- Final output
SELECT 
    ar.ProblemID,
    CAST(DATEDIFF(SECOND, v.LastInProgressTime, GETDATE()) / 3600.0 AS DECIMAL(10,1)) AS HoursSinceLastStatusChange,
    v.LastInProgressTime,
    GETDATE() AS SnapshotTime,
    0 AS SnapshotHour
FROM ActiveRCSTickets ar
JOIN ValidStatus v ON ar.ProblemID = v.ProblemID;
