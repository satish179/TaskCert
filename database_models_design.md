# Database Models Design for Django Task Management and Certification Platform

## Overview
This document outlines the database models and relationships for the Django-based task management and certification platform. The design includes models for users, mentors, tasks, submissions, exams, questions, results, and certificates, with appropriate fields, relationships, and constraints.

## Models

### 1. CustomUser
Extends Django's `AbstractUser` to include role-based access and mentor assignment.

**Fields:**
- `id` (AutoField, Primary Key)
- `username` (CharField, max_length=150, unique)
- `email` (EmailField, unique)
- `password` (CharField, max_length=128)
- `first_name` (CharField, max_length=30)
- `last_name` (CharField, max_length=150)
- `is_active` (BooleanField, default=True)
- `is_staff` (BooleanField, default=False)
- `date_joined` (DateTimeField, auto_now_add)
- `role` (CharField, max_length=10, choices=[('admin', 'Admin'), ('user', 'User')], default='user')
- `mentor` (ForeignKey to Mentor, on_delete=SET_NULL, null=True, blank=True)

**Relationships:**
- One-to-Many: CustomUser.mentor → Mentor (users assigned to mentors)
- One-to-Many: CustomUser.tasks → Task (tasks assigned to users)
- One-to-Many: CustomUser.submissions → Submission
- One-to-Many: CustomUser.results → Result
- One-to-Many: CustomUser.certificates → Certificate

**Constraints:**
- `username` and `email` must be unique
- `role` limited to 'admin' or 'user'

### 2. Mentor
Represents mentors who assign tasks and create exams.

**Fields:**
- `id` (AutoField, Primary Key)
- `name` (CharField, max_length=100)
- `email` (EmailField, unique)
- `bio` (TextField, blank=True)
- `specialization` (CharField, max_length=100, blank=True)
- `created_at` (DateTimeField, auto_now_add)

**Relationships:**
- One-to-Many: Mentor.assigned_tasks → Task (tasks assigned by mentors)
- One-to-Many: Mentor.created_exams → Exam
- One-to-Many: Mentor.users → CustomUser (reverse from CustomUser.mentor)

**Constraints:**
- `email` must be unique

### 3. Task
Represents tasks assigned to users by mentors.

**Fields:**
- `id` (AutoField, Primary Key)
- `name` (CharField, max_length=200)
- `due_date` (DateTimeField)
- `remarks` (TextField, blank=True)
- `status` (CharField, max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending')
- `assigned_by` (ForeignKey to Mentor, on_delete=CASCADE)
- `assigned_to` (ForeignKey to CustomUser, on_delete=CASCADE)
- `created_at` (DateTimeField, auto_now_add)

**Relationships:**
- Many-to-One: Task.assigned_by → Mentor
- Many-to-One: Task.assigned_to → CustomUser
- One-to-Many: Task.submissions → Submission

**Constraints:**
- `due_date` must be in the future (can be enforced in forms/views)
- `status` limited to predefined choices

### 4. Submission
Represents user submissions for tasks.

**Fields:**
- `id` (AutoField, Primary Key)
- `task` (ForeignKey to Task, on_delete=CASCADE)
- `submitted_by` (ForeignKey to CustomUser, on_delete=CASCADE)
- `submitted_at` (DateTimeField, auto_now_add)
- `content` (TextField)
- `status` (CharField, max_length=20, choices=[('submitted', 'Submitted'), ('reviewed', 'Reviewed'), ('approved', 'Approved')], default='submitted')
- `remarks` (TextField, blank=True)
- `score` (FloatField, null=True, blank=True)

**Relationships:**
- Many-to-One: Submission.task → Task
- Many-to-One: Submission.submitted_by → CustomUser

**Constraints:**
- `score` should be between 0 and 100 if provided (enforce in validation)
- `status` limited to predefined choices

### 5. Exam
Represents certification exams.

**Fields:**
- `id` (AutoField, Primary Key)
- `name` (CharField, max_length=200)
- `description` (TextField, blank=True)
- `due_date` (DateTimeField, null=True, blank=True)
- `created_by` (ForeignKey to Mentor, on_delete=CASCADE)
- `created_at` (DateTimeField, auto_now_add)

**Relationships:**
- Many-to-One: Exam.created_by → Mentor
- One-to-Many: Exam.questions → Question
- One-to-Many: Exam.results → Result
- One-to-Many: Exam.certificates → Certificate

**Constraints:**
- None specific

### 6. Question
Represents questions within exams.

**Fields:**
- `id` (AutoField, Primary Key)
- `exam` (ForeignKey to Exam, on_delete=CASCADE)
- `question_text` (TextField)
- `question_type` (CharField, max_length=20, choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False'), ('short_answer', 'Short Answer')], default='multiple_choice')
- `options` (JSONField, null=True, blank=True)  # For multiple choice options
- `correct_answer` (CharField, max_length=200)  # Or JSONField for complex answers

**Relationships:**
- Many-to-One: Question.exam → Exam

**Constraints:**
- `options` required for 'multiple_choice' type
- `correct_answer` must match question_type format

### 7. Result
Represents exam results for users.

**Fields:**
- `id` (AutoField, Primary Key)
- `user` (ForeignKey to CustomUser, on_delete=CASCADE)
- `exam` (ForeignKey to Exam, on_delete=CASCADE)
- `score` (FloatField)
- `passed` (BooleanField, default=False)
- `taken_at` (DateTimeField, auto_now_add)

**Relationships:**
- Many-to-One: Result.user → CustomUser
- Many-to-One: Result.exam → Exam

**Constraints:**
- `score` should be between 0 and 100
- Unique constraint on (user, exam) to prevent multiple results per exam per user

### 8. Certificate
Represents certificates issued to users upon exam completion.

**Fields:**
- `id` (AutoField, Primary Key)
- `user` (ForeignKey to CustomUser, on_delete=CASCADE)
- `exam` (ForeignKey to Exam, on_delete=CASCADE)
- `issued_date` (DateTimeField, auto_now_add)
- `certificate_number` (CharField, max_length=100, unique)

**Relationships:**
- Many-to-One: Certificate.user → CustomUser
- Many-to-One: Certificate.exam → Exam

**Constraints:**
- `certificate_number` must be unique
- Only issued if Result.passed is True (enforce in business logic)

## Key Relationships Summary
- Users are assigned to mentors (CustomUser.mentor → Mentor)
- Tasks are assigned to users by mentors (Task.assigned_to → CustomUser, Task.assigned_by → Mentor)
- Submissions are linked to tasks (Submission.task → Task)
- Exams contain questions (Question.exam → Exam)
- Results link users to exams (Result.user → CustomUser, Result.exam → Exam)
- Certificates are issued to users for exams (Certificate.user → CustomUser, Certificate.exam → Exam)

## Additional Notes
- All models include appropriate `created_at` or `auto_now_add` fields for auditing
- Foreign keys use CASCADE on_delete to maintain referential integrity
- Status fields use choices to limit valid values
- JSONField is used for flexible question options
- Scores are stored as FloatField for precision
- Unique constraints prevent duplicate results and certificates