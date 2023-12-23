-- create MySQL database and superuser  
-- login as root and GRANT PRIVILEDGES to the app Superuser

-- (.venv) mysql -u root -p
SET GLOBAL validate_password.length = 6;
SET GLOBAL validate_password.number_count = 0;
SET GLOBAL validate_password.mixed_case_count = 0;
SET GLOBAL validate_password.special_char_count = 0; 
SET GLOBAL validate_password.policy = LOW;
DROP DATABASE Hungry_Hippo_DB;
CREATE DATABASE Hungry_Hippo_DB;
CREATE USER 'chief'@'localhost' IDENTIFIED BY 'passw0rd';
GRANT ALL ON Hungry_Hippo_DB.* TO  chief@localhost;
SHOW VARIABLES LIKE 'validate_password%';
SHOW GRANTS FOR 'chief'@'localhost';

-- mysql user 'chief' now has all priviledges on database Hungry_Hippo_DB  