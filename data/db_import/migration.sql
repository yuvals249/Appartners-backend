-- Add is_yad2 column to users table
ALTER TABLE users ADD COLUMN is_yad2 BOOLEAN DEFAULT FALSE;

-- Add is_yad2 column to user_details table
ALTER TABLE user_details ADD COLUMN is_yad2 BOOLEAN DEFAULT FALSE;

-- Add is_yad2 column to apartments table
ALTER TABLE apartments ADD COLUMN is_yad2 BOOLEAN DEFAULT FALSE;

-- Remove house_number column from apartments table
ALTER TABLE apartments DROP COLUMN house_number;

-- Update API schema
-- Note: You'll need to manually update the api.yaml file to remove house_number
