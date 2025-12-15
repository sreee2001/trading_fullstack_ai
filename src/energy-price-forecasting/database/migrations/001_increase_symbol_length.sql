-- Database Schema Migration
-- Change commodities.symbol from VARCHAR(10) to VARCHAR(20)
-- Date: 2024-12-14
-- Reason: Support longer commodity symbols like BRENT_CRUDE (11 chars)

BEGIN;

-- Alter the symbol column to allow longer strings
ALTER TABLE commodities 
ALTER COLUMN symbol TYPE VARCHAR(20);

-- Verify the change
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'commodities' 
AND column_name = 'symbol';

COMMIT;

-- Expected output:
-- column_name | data_type      | character_maximum_length
-- ------------+----------------+-------------------------
-- symbol      | character varying | 20

