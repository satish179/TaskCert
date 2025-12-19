# Task Certification Platform - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Start the Server (if not already running)
```bash
cd c:\python\Scripts\application
python manage.py runserver
```

### 2. Access the Application
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

You'll be automatically redirected to the login page.

---

## 👤 Login Credentials

### Admin Account
- **URL**: http://127.0.0.1:8000/admin/
- **Username**: `admin`
- **Password**: `admin123`

### Test User Accounts
- **Username**: `user1`
- **Password**: `user123`
- **Mentor**: John Smith

---

OR

- **Username**: `user2`
- **Password**: `user123`
- **Mentor**: John Smith

---

## 📱 Main Pages

### For Regular Users
| Page | URL | Description |
|------|-----|-------------|
| Login | `/login/` | Sign in to your account |
| Register | `/register/` | Create new account |
| Dashboard | `/dashboard/` | View tasks, progress, submissions |
| Exams | `/exams/` | Take exams with timer |
| Certificates | `/certificates/` | View and download certificates |

### For Administrators
| Page | URL | Description |
|------|-----|-------------|
| Admin Panel | `/admin/` | Manage users, tasks, exams, results |

---

## 🔄 Sample Workflow

### As a Regular User:

1. **Login** with `user1` / `user123`
2. Go to **Dashboard** to see your tasks
3. View active tasks assigned by your mentor
4. **Submit** completed work for a task
5. Wait for admin approval
6. Once all tasks are complete, **take the Exam**
7. Pass the exam to **earn your Certificate**
8. **Download** the certificate as PDF

### As an Administrator:

1. Login to `/admin/` with `admin` / `admin123`
2. Navigate to **Submissions** section
3. Review pending submissions
4. **Approve** or **Reject** with feedback
5. View **Results** to see exam scores
6. View **Certificates** for completed users

---

## 🎯 Key Features to Explore

### ✅ Dashboard
- Real-time progress tracking
- Active task overview
- Submission history
- Mentor information

### 📝 Exam Features
- **Randomized Questions**: Each exam attempt shows different question order
- **Randomized Options**: Answer choices are shuffled
- **30-Minute Timer**: Countdown timer auto-submits when expired
- **Auto-Grading**: Instant results and pass/fail status

### 🏆 Certificates
- **Professional Design**: Gold certificate template
- **PDF Download**: One-click certificate download
- **Certificate ID**: Unique tracking number
- **Issue Date**: Date of certification

---

## 🔧 Useful Django Admin Commands

### Create a new user (via CLI)
```bash
python manage.py createsuperuser --username newadmin --email admin@example.com
```

### Create sample data
```bash
python populate_data.py
```

### Check system status
```bash
python manage.py check
```

### Access Django shell
```bash
python manage.py shell
# Then in shell:
from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all()
print(users)
```

---

## 🌐 API Endpoints

### Try API with curl or Postman

**Login (get session cookie)**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"user123"}'
```

**Get your profile**
```bash
curl http://127.0.0.1:8000/api/users/me/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

**Get your tasks**
```bash
curl http://127.0.0.1:8000/api/users/my_tasks/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

**Submit exam**
```bash
curl -X POST http://127.0.0.1:8000/api/results/submit_exam/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "exam_id": 1,
    "answers": {
      "q1": "Model View Template",
      "q2": "settings.py"
    }
  }'
```

---

## 🐛 Troubleshooting

### Problem: Login page shows error
**Solution**: 
- Clear browser cache
- Ensure server is running: `python manage.py runserver`

### Problem: Can't see dashboard
**Solution**:
- Verify you're logged in
- Check cookie/session settings in settings.py

### Problem: Exams page shows no exams
**Solution**:
- Run `python populate_data.py` to create sample exams
- Check admin panel to verify exam exists

### Problem: Timer doesn't work
**Solution**:
- Enable JavaScript in browser
- Check browser console for errors (F12)

---

## 📊 Sample Test Data

The system comes pre-populated with:

**Mentors (2):**
- John Smith (Web Development)
- Sarah Johnson (Cloud & DevOps)

**Users (2):**
- user1 (Alice Developer) - Assigned to John Smith
- user2 (Bob Coder) - Assigned to John Smith

**Tasks (4):**
1. Create Login Functionality - Due in 7 days
2. Create Registration Page - Due in 14 days
3. Implement Dashboard - Due in 21 days
4. Add Task Submission Feature - Due in 28 days

**Exams (1):**
- Django Fundamentals Exam - 5 Questions

---

## 📝 Next Steps

1. **Create your own users** in the registration page
2. **Create new tasks** via Django admin
3. **Assign tasks** to specific users
4. **Review submissions** in admin panel
5. **Create new exams** with custom questions
6. **Monitor progress** in admin dashboard

---

## 📚 Documentation

Full documentation available in: **README.md**

---

## ⚡ Performance Tips

- The database uses SQLite (good for development)
- For production, switch to PostgreSQL
- Enable caching for better performance
- Use Gunicorn/uWSGI for production server

---

## 🎓 Learning Path for Users

1. Complete "Create Login Functionality" task
2. Wait for admin approval
3. Complete "Create Registration Page" task
4. Continue until all tasks done
5. Take the exam
6. Download your certificate!

---

## 💡 Pro Tips

- **For Admins**: Use Django admin interface for bulk operations
- **For Devs**: API endpoints available for mobile app integration
- **For Users**: Check dashboard daily for task updates

---

**Happy Learning! 🎉**

For more help, check the README.md file or API documentation.
