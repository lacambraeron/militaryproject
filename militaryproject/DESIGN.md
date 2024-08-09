I used the code from the "finance" problem set as a framework and changed and implemented a few ideas

The project required a few things:

Library: a page that had all the tasks a user needed to accomplish, and the tasks Task Training Guide
Certification process: a process that tracks a user's statement certifying that they've accomplished the Pre-requisites of a task, any Auxiliary traning, and Evaluation
(Although the steps for each task need not be tracked, ultimately, just that the task be certified)
Tracking progress: Keeping track of the date when the user certified accomplishing the task
Admin Dashboard: An admin account that can monitor every user's task completion

Database:
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS 'tasks' ('id' TEXT NOT NULL, 'description' TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS 'completed' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER, description TEXT, timestamp DATETIME, FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'progress' NUMERIC NOT NULL DEFAULT 00.00, 'first_name' TEXT NOT NULL, 'last_name' TEXT NOT NULL);

Very similar to how Finance is implemented

At this time, while the Air Force has a directory that contains what's in the library, it is very obscure, and hard to navigate.
In addition, the Air Force has no system that has these 3 combined.

The Library page was simple, I wanted to create a table that had had the task's task code, task name/description, and links to the files for those codes.
So in the final/static/TTG directory, all the pdf files can be found. Each task name/description is a hyperlink to those files.

In the certification process, a user selects a task from the drop down menu, has to check all three boxes and hit submit for the certification process to succeed.
The main thing here is that the user must know that they need to do all three (even if they can just click the boxes anyway, however, this relies on the user's integrity)
The code checks if any are missing or no task selected, and returns an error if any requirement is missing.
Once the user hits submit, the database is updated to track the datetime of the certification, the task (that was just certified) disappears from the drop down list of required tasks.
And it is recorded in the 'completed' table 
with the following schema
CREATE TABLE IF NOT EXISTS 'completed' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER, description TEXT, timestamp DATETIME, FOREIGN KEY(user_id) REFERENCES users(id));

I could in the future, learn how to have supervisor/trainee roles, where a supervisor certifies this for a trainee instead, but I haven't figured out how to implement that. For now, 
a user will have to track their own training and the supervisors rely on their trainee's integrity

In /progress, the page shows a table of the task and the date of certification. Again, very similar to finance's implementation
All I did here was to save the SQL query into a variable and passed it through a template

The admin dashboard was trickier, because using the two databases, I had to make do of what I had, but still inspired by 'finance' as my framework.
I had to use this SQL command to create a table that combined users and the completion table to show the user's information and certification for each task:
  rows = db.execute("""SELECT
    users.username,
    users.first_name,
    users.last_name,
    MAX(CASE WHEN completed.description = 'Air Transportation' THEN completed.timestamp END) AS task_1_timestamp,
    MAX(CASE WHEN completed.description = 'Career Progression' THEN completed.timestamp END) AS task_1_1_timestamp,
    MAX(CASE WHEN completed.description = 'Organizational Structure' THEN completed.timestamp END) AS task_1_2_timestamp,
    MAX(CASE WHEN completed.description = 'Types and Descriptions of Transport Aircrafts' THEN completed.timestamp END) AS task_1_3_timestamp,
    MAX(CASE WHEN completed.description = 'Locate and Reference Transportation Forms, Publications, and Technical Orders' THEN completed.timestamp END) AS task_1_4_timestamp,
    MAX(CASE WHEN completed.description = 'Inspect, Inventory, and Store 463L Pallets, Nets, and Tie Down Equipment' THEN completed.timestamp END) AS task_1_5_timestamp,
    MAX(CASE WHEN completed.description = 'Build Single Pallet' THEN completed.timestamp END) AS task_1_6_timestamp,
    MAX(CASE WHEN completed.description = 'Identify Types of Shoring' THEN completed.timestamp END) AS task_1_7_timestamp,
    MAX(CASE WHEN completed.description = 'Perform Spotter - Chocker Duties' THEN completed.timestamp END) AS task_1_8_timestamp,
    MAX(CASE WHEN completed.description = 'Vehicle Inspections' THEN completed.timestamp END) AS task_1_9_timestamp,
    MAX(CASE WHEN completed.description = 'Perform Engine Running Off-load On-load (ERO) Operations' THEN completed.timestamp END) AS task_1_10_timestamp,
    MAX(CASE WHEN completed.description = 'Air Transportation Information Systems' THEN completed.timestamp END) AS task_1_11_timestamp,
    MAX(CASE WHEN completed.description = 'Compliance-Evaluation Fundamentals' THEN completed.timestamp END) AS task_1_12_timestamp
FROM
    users
LEFT JOIN
    completed ON users.id = completed.user_id
GROUP BY
    users.username, users.first_name, users.last_name""")

Initially, I was going to create a table that had every task as my header and every cell in the table as the date, however, I learned that sqlite cannot update specific cells one at a time. So I had to look up how I may just be able to combine these two tables.

Yes, this looks harder since I used the task name/description instead of the task code, but with the code I already have, it felt better do it this way.

As for html design. I chose to keep it simple, with the navbar, main content, and footer. As for the "unclassified" banner, DOD apps/websites are usually labeled this way.
The bulldog logo is a known insignia for Air Transportation Specialists also known as "Port Dawgs"


