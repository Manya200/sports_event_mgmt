# Sport Event Management System

## Overview
The **Sport Event Management System** is a Django-based web application designed to manage sports events efficiently. This project supports dynamic user login for different roles (such as Event Organizer, Venue Manager, and Participant) and includes functionalities like event creation, registration, payment processing, and more.

## Prerequisites
Before setting up the project, ensure you have the following installed:
- Python 3.x
- pip
- Virtualenv (optional but recommended)
- SQLite (default; can be configured for PostgreSQL/MySQL)

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/sport-event-management.git](https://github.com/Manya200/sports_event_mgmt.git
   cd sport-event-management
   ```

2. **Create a Virtual Environment**
   Create and activate a virtual environment:
   ```bash
   python -m venv venv
   ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install Dependencies
   Install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply Migrations
   Generate and apply the database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a Superuser (Optional)**
   To access the Django admin interface:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server**
   Start the Django development server:
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/` to view the project.

## Project Structure
A brief overview of the project structure is shown below:
```
sport-event-management/
├── events/
│   ├── migrations/
│   ├── templates/
│   │   ├── registration/
│   │   │   └── register_new_user.html
│   │   └── dashboard/
│   │       ├── participant_dashboard.html
│   │       ├── event_organizer_dashboard.html
│   │       └── dashboard.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── sports_event_mgmt/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
└── requirements.txt
```

## Running the Project
Once the installation and setup steps are complete, run the following command to start the development server:
```bash
python manage.py runserver
```
Then, open your browser and visit:
```
http://127.0.0.1:8000/
```

---

Happy coding!

