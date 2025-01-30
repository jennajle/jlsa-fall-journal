## Completed Work

- Database Integration: Connected the API server to MongoDB database 
- Masthead page
- People
    - Added some role functionality
       - Clearing list of all roles, add roles to people
    - Added manuscript workflow
        - Keeping track of role history
    - CRUD Operations for general person management
        - Create, Read, Update, and Delete
- Manuscripts
    - Basic manuscript page 

## Goals For This Semester

 - Add role based control and access
    Steps: 
    - Add permission checks in create, update, delete, and read() to ensure only authorized users can modify accounts.
    - Add additional methods that have not been implemented yet (ex. View, deleting permissions)
    Relevant requirements: 
    - Users can edit and delete their own accounts.
    - Only the editor and managing editor(s) have create / update / delete permissions for the accounts of others.
    - A listing of all people is available, but only to the editor and managing editor(s).
    - Only the editor and managing editor(s) see all manuscripts; everyone else only sees "their own." That means manuscripts for which they are the author or referee.
    - These texts can be edited from the client application, but only by the editor and managing editor(s).
- Add manuscript workflow with proper role assignment at each step 
    Steps: 
    1) Work on linear flows 
        - Start → Referee Review → Copy Edit → Author Review → Formatting → Published
        - Referee Review → Author Revisions → Editor Review 
    2) Add in other remaining functionality 
        - Add/remove referees 
        - Rejection process 
    Relevant requirements: 
    - Manuscripts can flow through the system according to this chart.
    - Submitting a manuscript creates an account with the role of author.
    - Assigning a referee to a manuscript adds the referee role to that person.
- Create intuitive front end interface 
    Steps: 
    - Design and implement a user-friendly frontend dashboard that provides clear visualizations of manuscript statuses, including interactive elements for improved navigation and usability.
    Relevant requirements:
    - A dashboard will present the manuscripts in visual form.
- Improve Frontend for Journal Masthead Generation
    Steps: 
    - Develop a frontend component that dynamically fetches and displays the masthead using the stored database information.
    Relevant requirements: 
    - Enable automatic journal masthead generation from the database.
    - All large runs of text in the system, such as "About this Journal" or "Submission Guidelines," are stored in the database.
