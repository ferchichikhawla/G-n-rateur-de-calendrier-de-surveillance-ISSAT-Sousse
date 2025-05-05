# Caendrier-algo

This project is a Django-based scheduling application for managing teacher assignments and session schedules. It includes features for importing teacher and session data from Excel files, running scheduling algorithms, and exporting schedules as Excel or PDF files.

## Features

- Import teacher and session data via Excel uploads.
- Run scheduling algorithm to assign teachers to sessions.
- Export schedules as Excel files or individual teacher PDF timetables.
- Admin dashboard with file management and teacher list.
- Download individual teacher schedules from the dashboard.

## Setup

1. Create and activate a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Run the development server:

```bash
python manage.py runserver
```

5. Access the admin dashboard at `http://127.0.0.1:8000/dashboard/`.

## Usage

- Use the dashboard to upload teacher and session Excel files.
- Generate and download schedules.
- View and download individual teacher schedules.

## Notes

- Ensure you have the required Python packages installed as per requirements.txt.
- The frontend integration is done via API calls; see frontend-integration.md for details.
- Customize the admin dashboard templates and styles as needed.

## License

This project is licensed under the MIT License.
