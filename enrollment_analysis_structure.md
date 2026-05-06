| Structural Issue                                                                           | Where It Appears                                                                 | Why It Matters                                                                                                                                                    | Layer-Design Concern                                                                  | Refactor Priority | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ----------------- |
| Global constants and sample state are mixed into the main backend file                     | `DB_PATH`, `SNAPSHOT_PATH`, `CURRENT_STUDENT`, statuses, `AVAILABLE_COURSE_KEYS` | As the project grows, it becomes harder to tell what is real app state, sample data, or configuration.                                                            | Config/sample data is mixed with database and service behavior.                       | Medium            |
| Database connection logic depends on global path                                           | `connect`                                                                        | This makes the database location harder to change or test because every function depends on the same global path.                                                 | Database setup should be isolated in a database layer.                                | Medium            |
| Seeding mixes database work with sample course-key data                                    | `seed_sample_data`                                                               | The function inserts rows, but it also depends on predefined course/enrollment sample data. This can make future real data harder to separate from practice data. | Database class should insert data, but sample data should be treated as setup/config. | Medium            |
| Some database functions also enforce service-level rules                                   | `get_course_by_key`, `get_student_enrollments`, `get_student_enrollment_history` | These are mostly database queries, but they also decide things like returning `None` or `[]` when input is missing and filtering only enrolled records.           | Small service decisions are embedded in database functions.                           | Medium            |
| Enrollment action combines validation, key lookup, database insert, and reactivation logic | `enroll_with_key`                                                                | This is one of the biggest mixed-layer problems. If enrollment rules change, the SQL function also has to change.                                                 | Cross-layer mixing: service rule + database write.                                    | High              |
| Soft unenroll combines student action meaning with SQL update                              | `soft_unenroll_student`                                                          | The database update is simple, but the decision to “soft unenroll” by changing status is a business rule.                                                         | Service should decide the action; database should only update the row.                | High              |
| Summary counting depends on service meaning of statuses                                    | `get_student_summary`                                                            | This function interprets records and turns them into dashboard counts. That is not raw database work, so keeping it separate improves clarity.                    | Belongs in service layer.                                                             | Medium            |
| Export snapshot combines database reads, current student state, and JSON writing           | `export_database_snapshot`                                                       | It pulls from multiple sources and writes a file, so it is harder to classify and test as the project grows.                                                      | Cross-layer mixing: database reads + config/sample state + file export.               | Medium            |
| Main runner performs setup, student action, reporting, and export in one flow              | `main`                                                                           | It is useful for practice, but it mixes testing, demo behavior, setup, and application actions.                                                                   | Should eventually be separated from service/database design.                          | Low-Medium        |
| SQL statements are spread across many procedural functions                                 | `SELECT`, `INSERT`, `UPDATE` throughout the file                                 | As more features are added, scattered SQL makes it harder to update table structure or reuse database behavior.                                                   | SQL should be centralized in a database class.                                        | High              |
| Status strings are used as business meaning across layers                                  | `STATUS_ENROLLED`, `STATUS_UNENROLLED`, filtering and summary logic              | The same values control database storage and service meaning. If more statuses are added, multiple functions may need updates.                                    | Status constants are config, but status decisions belong in service.                  | Medium            |
| Row conversion is database helper logic but supports many functions                        | `rows_to_dicts`                                                                  | This is not a major problem, but it shows repeated database-output formatting.                                                                                    | Fits better as a database helper method.                                              | Low               |

##Refactoring Plan

1. Short summary of future architecture

The safest plan is to split the backend into a database class and a service class. The database class should only handle SQLite connections, table creation, queries, inserts, and updates. The service class should handle what those actions mean, like enrolling with a key, soft unenrolling, summary counting, and dashboard logic.

2. Where each part should go
Current Function / Responsibility	Future Location	Why
DB_PATH, SNAPSHOT_PATH	Config/constants	These are file paths, not service or database behavior.
STATUS_ENROLLED, STATUS_UNENROLLED	Config/constants or service	These are status values, but the service should decide what they mean.
CURRENT_STUDENT	Sample/demo data	This should not be mixed into the main backend logic long term.
AVAILABLE_COURSE_KEYS	Sample/demo data	This is starter data, not core service behavior.
connect	Database class	It opens the SQLite connection.
create_tables	Database class	It creates database tables.
seed_sample_data	Database class, using sample data	It writes starter data into the database.
rows_to_dicts	Database class/helper	It formats database rows.
get_available_course_keys	Database class	It reads course key rows from SQLite.
get_course_by_key	Database class	It looks up a course row by key.
get_student_enrollments	Database class	It retrieves enrolled records.
get_student_enrollment_history	Database class	It retrieves all records for one student.
get_student_course_record	Database class	It retrieves one enrollment record.
enroll_with_key	Service class, with database calls	It includes validation, key rules, and reactivation meaning.
soft_unenroll_student	Service class, with database calls	The service should decide what soft unenroll means.
get_student_summary	Service class	It counts records and gives dashboard meaning.
get_all_enrollment_records	Database class	It reads all enrollment records from SQLite.
export_database_snapshot	Separate export/helper function	It combines database reads and JSON writing, so it should stay separate.
main	Demo/test runner	It should only run the program flow, not own logic.
3. Simple step-by-step refactor order
Step	What to Do	Why
1	Separate constants and sample data mentally first.	This makes it clearer what is real logic versus setup data.
2	Create a database class plan.	This class will own SQLite work only.
3	Move connection, table creation, seeding, and query functions into the database class.	These are the safest functions to move first because they are mostly database-focused.
4	Create a service class plan.	This class will own student enrollment meaning and dashboard logic.
5	Move get_student_summary into the service class.	It already acts like service logic.
6	Split enroll_with_key.	Keep validation and enrollment meaning in service, and keep database insert/update in database.
7	Split soft_unenroll_student.	Service decides the action, database updates the row.
8	Keep export snapshot separate.	It is not really database or service because it writes JSON output.
9	Keep main as a simple test/demo runner.	It should only call the classes to check behavior.
4. What should not change yet

Do not change the database tables yet.
Do not change the enrollment behavior yet.
Do not change the sample data yet.
Do not add UI features.
Do not add new app features.
Do not rewrite the logic all at once.

5. Implementation prompt to use later
I approved the backend refactor plan. Please now help me refactor the procedural student enrollment backend into an object-oriented layered design.

Please keep the behavior the same.

Create a database class that owns:
- SQLite connection logic
- table creation
- sample data seeding
- row conversion helpers
- course queries
- enrollment record queries
- enrollment insert/update operations
- soft status updates

Create a service class that owns:
- enrollment-key validation
- student enrollment actions
- reactivation meaning
- soft unenroll meaning
- student summary counting
- dashboard-level meaning

Keep constants and sample data separate from the main logic where possible.

Keep export snapshot logic separate because it combines database reads and JSON writing.

Keep the main runner simple and only use it to test the same behavior as before.

Do not add new features.
Do not add UI code.
Do not change the database schema unless absolutely necessary.
Do not change the expected outputs.
