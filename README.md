# Task Certification Platform

A comprehensive Django web application for task management and online certification with dual authentication (users and administrators), mentor-guided learning, and automated assessment.

## Features

### User Management
- **User Registration**: Self-registration for learners with automatic mentor assignment
- **Dual Authentication**: 
  - Regular users: Registration + Login
  - Administrators: Pre-created accounts with login-only access
- **User Roles**: Role-based access control (User vs Admin)

### Task Management System
- **Task Assignment**: Mentors assign tasks to users
- **Task Tracking**: Users can view assigned tasks with due dates
- **Task Submission**: Users submit completed work for admin verification
- **Progressive Workflow**: Admin auto-assigns next task after approval

### Exam Module
- **Online Exams**: Customizable exams with 10-20 questions
- **Question Types**: Multiple choice, True/False, Short answer
- **Randomization**: Questions and options randomized via JavaScript
- **Countdown Timer**: Real-time exam timer with JavaScript
- **Auto-Grading**: Automatic scoring and result calculation

### Certification System
- **Certificate Generation**: Auto-generated upon exam pass
- **PDF Download**: Download certificates in professional PDF format
- **Certificate Customization**: Institution/company branding support

### Notifications & Alerts
- **Due Date Monitoring**: Alerts for approaching/overdue tasks
- **Dashboard Alerts**: Visible notifications on user dashboard

### Admin Dashboard
- **User Management**: View all users, their progress, and roles
- **Task Oversight**: Track all assigned tasks and submissions
- **Submission Review**: Verify submitted work and assign scores
- **Exam Analytics**: Monitor exam performance and results
- **System Analytics**: Overall platform statistics

## Project Structure

```
application/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── populate_data.py
│
├── application/
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application
│
├── restapi/
│   ├── models.py                # Database models
│   ├── views.py                 # View functions
│   ├── serializers.py           # DRF serializers
│   ├── urls.py                  # API routes
│   ├── admin.py                 # Admin configuration
│   ├── tests.py                 # Unit tests
│   └── migrations/              # Database migrations
│
├── templates/
│   ├── base.html                # Base template
│   ├── navbar.html              # Navigation bar
│   ├── sidebar.html             # Sidebar menu
│   ├── alerts.html              # Alert messages
│   ├── footer.html              # Footer
│   ├── registration/
│   │   ├── login.html           # Login page
│   │   └── register.html        # Registration page
│   ├── tasks/
│   │   └── dashboard.html       # User dashboard
│   ├── exams/
│   │   └── exams.html           # Exam page with timer
│   └── certificates/
│       └── certificates.html    # Certificates page
│
├── static/
│   ├── css/                     # Custom CSS
│   ├── js/                      # Custom JavaScript
│   └── images/                  # Images
│
└── media/
    ├── certificates/           # Generated certificates
    ├── profile_pics/           # User profile images
    └── task_submissions/       # Submitted files
```

## Technology Stack

- **Backend**: Django 6.0
- **API**: Django REST Framework 3.14
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Database**: SQLite3
- **JavaScript**: Vanilla JS (timers, randomization, PDF generation)
- **PDF Generation**: html2pdf.js (client-side)

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Step 1: Install Dependencies
```bash
cd c:\python\Scripts\application
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

Or use the pre-created admin account:
- **Username**: admin
- **Password**: admin123

### Step 4: Populate Sample Data
```bash
python populate_data.py
```

This creates:
- 2 sample mentors
- 2 sample users (user1, user2 / password: user123)
- 4 sample tasks
- 1 sample exam with 5 questions

### Step 5: Start Development Server
```bash
python manage.py runserver
```

Access the application at: **http://127.0.0.1:8000/**

## User Accounts

### Pre-configured Accounts

**Admin Account:**
- Username: `admin`
- Password: `admin123`
- Role: Administrator (staff user)

**Sample User Accounts:**
- Username: `user1` / Password: `user123`
- Username: `user2` / Password: `user123`
- Role: Regular User
- Mentor: John Smith (auto-assigned)

## Usage Guide

### For Regular Users

1. **Register/Login**
   - Click "Register" for new users
   - Complete registration form
   - Auto-assigned to first available mentor
   - Login with credentials

2. **Dashboard**
   - View active, completed, and overdue tasks
   - Monitor progress percentage
   - See recent submissions
   - View mentor information

3. **Task Management**
   - View assigned tasks with due dates
   - Submit completed work
   - Track submission status

4. **Exams**
   - View available exams
   - Start exam (questions randomized)
   - 30-minute countdown timer
   - Submit answers for auto-grading

5. **Certificates**
   - View earned certificates
   - Preview certificate design
   - Download as PDF

### For Administrators

1. **Admin Dashboard**
   - Login with admin credentials
   - Access admin panel at `/admin/`

2. **Manage Users**
   - View all registered users
   - Monitor user progress
   - Assign roles

3. **Review Submissions**
   - View pending task submissions
   - Approve or reject with feedback
   - Auto-assign next task on approval

4. **Manage Exams**
   - Create new exams
   - Add exam questions
   - Review exam results

## API Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout

### Users
- `GET /api/users/` - List all users
- `GET /api/users/me/` - Get current user
- `GET /api/users/my_tasks/` - Get user's tasks
- `GET /api/users/overdue_tasks/` - Get overdue tasks
- `GET /api/users/my_submissions/` - Get user's submissions
- `GET /api/users/my_certificates/` - Get user's certificates

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create task
- `POST /api/tasks/{id}/mark_completed/` - Mark task complete

### Submissions
- `GET /api/submissions/` - List submissions
- `POST /api/submissions/` - Create submission
- `POST /api/submissions/{id}/approve/` - Admin approve submission
- `POST /api/submissions/{id}/reject/` - Admin reject submission

### Exams & Results
- `GET /api/exams/` - List exams
- `GET /api/questions/` - List questions
- `POST /api/results/submit_exam/` - Submit exam answers
- `GET /api/results/` - Get user results

### Certificates
- `GET /api/certificates/` - List certificates
- `GET /api/certificates/{id}/download/` - Get certificate data

## Key Features Implementation

### Question Randomization (JavaScript)
```javascript
// Questions are shuffled using Fisher-Yates algorithm
// Options within questions are also randomized
```

### Exam Timer (JavaScript)
```javascript
// 30-minute countdown timer
// Auto-submits when time expires
// Real-time display in MM:SS format
```

### Certificate PDF Generation
```javascript
// Client-side HTML to PDF conversion
// Uses html2pdf.js library
// Professional certificate template
```

### Progressive Task Assignment
```python
# Admin approves submission
# Next pending task auto-assigned to user
# Tracks completion workflow
```

## Database Models

### CustomUser
- Extends Django's AbstractUser
- Added fields: role, mentor

### Mentor
- name, email, bio, specialization
- Has many users

### Task
- name, due_date, remarks, status
- assigned_by (Mentor), assigned_to (User)
- Statuses: pending, in_progress, completed

### Submission
- task, submitted_by, content, status
- Score tracking and remarks
- Statuses: submitted, reviewed, approved

### Exam
- name, description, due_date, created_by
- Has many questions

### Question
- exam, question_text, options (JSON)
- question_type, correct_answer

### Result
- user, exam, score, passed
- taken_at timestamp

### Certificate
- user, exam, issued_date
- certificate_number (unique)

## Security Considerations

✅ **Implemented:**
- User authentication required for protected views
- CSRF protection on forms
- Role-based access control
- Password hashing (Django default)
- SQL injection prevention (ORM)

⚠️ **For Production:**
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use environment variables for secrets
- Set up HTTPS/SSL
- Configure secure database
- Implement rate limiting
- Add input validation
- Set up logging and monitoring

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'restapi'"
**Solution**: Ensure you're in the correct directory and have run migrations.

### Issue: Port 8000 already in use
**Solution**: Use different port:
```bash
python manage.py runserver 8080
```

### Issue: Database errors
**Solution**: Reset database:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python populate_data.py
```

### Issue: Static files not loading
**Solution**: Collect static files:
```bash
python manage.py collectstatic --noinput
```

## Performance Optimization

- Database indexing on frequently queried fields
- Pagination for large result sets (10 items per page)
- Lazy loading for related objects
- Query optimization with select_related/prefetch_related

## Future Enhancements

- [ ] Real-time notifications using WebSockets
- [ ] Email notifications for submissions
- [ ] Advanced reporting and analytics
- [ ] Bulk task assignment
- [ ] Task templates
- [ ] Peer review system
- [ ] Discussion forums
- [ ] Mobile app (Flutter/React Native)
- [ ] Video tutorials integration
- [ ] AI-based question generation
- [ ] Advanced certificate designs
- [ ] Certificate validation system

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: December 10, 2024  
**Status**: Ready for Development/Testing
