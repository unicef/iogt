-- check counts
SELECT
    email,
    is_staff,
    COUNT(*) AS counts
FROM iogt_users_user
WHERE email IS NOT NULL
  AND email != ''
GROUP BY email, is_staff
HAVING COUNT(*) > 1
ORDER BY email, is_staff;


-- check emails
WITH duplicates AS (
    SELECT
        id,
        email,
        is_staff,
        ROW_NUMBER() OVER (
            PARTITION BY email, is_staff
            ORDER BY id
        ) AS rn,
        COUNT(*) OVER (
            PARTITION BY email, is_staff
        ) AS duplicate_count
    FROM iogt_users_user
    WHERE email IS NOT NULL
      AND email != ''
),
updates AS (
    SELECT
        id,
        email AS old_email,
        is_staff,
        rn,
        duplicate_count,
        SPLIT_PART(email, '@', 1)
        || '+' || LPAD((rn - 1)::text, 2, '0')
        || '@'
        || SPLIT_PART(email, '@', 2) AS new_email
    FROM duplicates
    WHERE duplicate_count > 1
      AND rn > 1
)
SELECT
    id,
    old_email,
    new_email,
    is_staff,
    rn,
    duplicate_count
FROM updates
ORDER BY old_email, is_staff, rn;



-- update emails
WITH duplicates AS (
    SELECT
        id,
        email,
        is_staff,
        ROW_NUMBER() OVER (
            PARTITION BY email, is_staff
            ORDER BY id
        ) AS rn,
        COUNT(*) OVER (
            PARTITION BY email, is_staff
        ) AS duplicate_count
    FROM iogt_users_user
    WHERE email IS NOT NULL
      AND email != ''
),
updates AS (
    SELECT
        id,
        email,
        is_staff,
        rn,
        duplicate_count,
        SPLIT_PART(email, '@', 1)
        || '+' || LPAD((rn - 1)::text, 2, '0')
        || '@'
        || SPLIT_PART(email, '@', 2) AS new_email
    FROM duplicates
    WHERE duplicate_count > 1
      AND rn > 1
)
UPDATE iogt_users_user u
SET email = updates.new_email
FROM updates
WHERE u.id = updates.id;