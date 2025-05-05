# Frontend and Backend Integration Instructions

This document provides detailed instructions and example code snippets to integrate your existing frontend (Electron app) with the Django backend.

---

## 1. User Authentication

### Login

Send a POST request to `/users/login/` with JSON body containing email and password.

Example:

```js
async function login(email, password) {
  const response = await fetch('http://localhost:8000/users/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  if (data.status === 'success') {
    // Navigate to admin dashboard
    window.electronAPI.goToDashboard();
  } else {
    alert('Login failed: ' + data.message);
  }
}
```

### Registration

Send a POST request to `/users/register/` with JSON body containing registration details.

Example:

```js


async function register(userData) {
  const response = await fetch('http://localhost:8000/users/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });
  const data = await response.json();
  if (data.status === 'success') {
    alert('Registration successful. Please login.');
  } else {
    alert('Registration failed: ' + data.message);
  }
}
```

---

## 2. File Upload (Teachers and Sessions)

Use `FormData` to upload Excel files to `/teacher/` and `/sessions/` endpoints.

Example for uploading teacher file:

```js
async function uploadTeacherFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/teacher/', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  if (data.status === 'success') {
    alert(`Successfully imported ${data.count} teachers.`);
  } else {
    alert('Import failed: ' + data.message);
  }
}
```

Similarly for sessions:

```js
async function uploadSessionFile(file, teacherCols = []) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('teacher_cols', teacherCols.join(','));

  const response = await fetch('http://localhost:8000/sessions/', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  if (data.success) {
    alert(data.status);
  } else {
    alert('Import failed: ' + (data.errors ? data.errors.join(', ') : 'Unknown error'));
  }
}
```

---

## 3. Trigger Assignment and Display Results

Send a POST request to `/assignements/` to trigger assignment and get results.

Example:

```js
async function triggerAssignment() {
  const response = await fetch('http://localhost:8000/assignements/', {
    method: 'POST'
  });

  const data = await response.json();
  if (data.status === 'success') {
    displayAssignmentResults(data.results);
  } else {
    alert('Assignment failed: ' + data.message);
  }
}

function displayAssignmentResults(results) {
  // Update your UI with sessions, teachers, and verification data
  console.log(results);
  // Implement UI rendering logic here
}
```

---

## 4. Download Exported Files

Provide buttons or links to download Excel and PDF files from `/generate/` and `/timetable/`.

Example:

```js
function downloadExcel() {
  window.open('http://localhost:8000/generate/', '_blank');
}

function downloadPDF() {
  window.open('http://localhost:8000/timetable/', '_blank');
}
```

---

## Notes

- Replace `http://localhost:8000` with your backend server URL if different.
- Ensure CORS is configured on the backend to allow requests from your frontend origin.
- Handle authentication tokens or sessions as needed for secure endpoints.
- Integrate these functions into your existing frontend event handlers and UI components.

---

If you want, I can help you implement these changes directly into your frontend files.
