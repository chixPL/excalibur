# Excalibur
A school register application written in Python using Qt5.

<p align="center">
    <img src="/images/logo.png" alt="excalibur-logo" width="256px" height="256px">
</p>

## Functionality
* Support for n number of classes, each having n students and grades.
* Support for multiple users with three types of roles: Admin, Teacher and Student, each with their own panel.
* Teacher's panel for overseeing each class, with the ability to add, edit or remove grades and statistical functions.
* Admin panel for adding, editing and removing classes, students and teachers.
* Student panel for viewing grades and their averages.
* Support for semester and final grades.
* "Forgot password" function with email verification.
* Clock in the top right corner.

## Quick start  
### Requirements
* Python 3.6 or newer
* PyQt5 and psycopg2 libraries installed
* PostgreSQL 14.6 or newer (by default the setup script uses the default database *postgres* to create a new one for the app)
### Installation
1. Clone the repository
2. Install the required dependencies:
    * `pip install -r requirements.txt`
3. Run the setup script:
    * `python setup.py`
    , then follow the instructions in the app.
4. After the setup script is done, open the app:
    * `python main.py`

Excalibur will notice that there are no classes and give you an introduction to help get you started.

## Screenshots
### Main window
<img src="/images/screenshots/main.png" alt="main">

### Login window
<img src="/images/screenshots/login.png" alt="login">

### Add note window
<img src="/images/screenshots/addnote.png" alt="add-note">