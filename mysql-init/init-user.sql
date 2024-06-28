-- Create the user with mysql_native_password authentication
DROP USER IF EXISTS 'imtiaz'@'%';
CREATE USER 'imtiaz'@'%' IDENTIFIED WITH mysql_native_password BY 'as';
GRANT ALL PRIVILEGES ON *.* TO 'imtiaz'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
