import logging
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, get_user_model, logout as auth_logout
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta, datetime
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Mentor, Task, Submission, Exam, Question, Result, Certificate, Topic, SampleQuestion, ExamAttempt, UserActivityLog, CustomUser, Resource, ForumPost, ForumComment

@login_required
def leaderboard_view(request):
    # Fetch top 20 users by points
    leaders = CustomUser.objects.filter(role='user').order_by('-points')[:20]
    return render(request, 'leaderboard.html', {'leaders': leaders})

from .serializers import (
    UserSerializer, UserRegistrationSerializer, MentorSerializer,
    TaskSerializer, SubmissionSerializer, ExamSerializer,
    QuestionSerializer, ResultSerializer, CertificateSerializer
)

User = get_user_model()


def _generate_unique_username(first_name: str = '', last_name: str = '') -> str:
    base = slugify(f"{(first_name or '').strip()}{(last_name or '').strip()}")
    if not base:
        base = slugify((first_name or '').strip()) or slugify((last_name or '').strip()) or 'user'
    base = base.replace('-', '')

    candidate = base
    counter = 2
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{counter}"
        counter += 1
    return candidate


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_staff

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log Activity
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
                
            UserActivityLog.objects.create(
                user=user,
                activity_type='login',
                ip_address=ip,
                details='API Login'
            )
            
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Log Activity
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
                
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='logout',
                ip_address=ip,
                details='API Logout'
            )
        except Exception:
            pass # logging should not block logout
            
        return Response({'message': 'Logout successful'})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_tasks(self, request):
        now = timezone.now()
        tasks = Task.objects.filter(assigned_to=request.user, due_date__lt=now, status__in=['pending', 'in_progress'])
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        submissions = Submission.objects.filter(submitted_by=request.user)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_results(self, request):
        results = Result.objects.filter(user=request.user)
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_certificates(self, request):
        certificates = Certificate.objects.filter(user=request.user)
        serializer = CertificateSerializer(certificates, many=True)
        return Response(serializer.data)

class MentorViewSet(viewsets.ModelViewSet):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [IsStaffOrReadOnly]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        task = self.get_object()
        if task.assigned_to == request.user:
            task.status = 'completed'
            task.save()
            return Response({'status': 'task marked as completed'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        task_id = request.data.get('task')
        content = request.data.get('content')
        
        task = Task.objects.get(id=task_id)
        submission = Submission.objects.create(
            task=task,
            submitted_by=request.user,
            content=content,
            status='submitted'
        )
        serializer = self.get_serializer(submission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        submission = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        submission.status = 'approved'
        submission.score = request.data.get('score', 100)
        submission.save()
        
        # Mark task as completed and assign next task
        task = submission.task
        task.status = 'completed'
        task.save()
        
        # Auto-assign next task based on current task completion
        next_task = Task.objects.filter(
            assigned_to=submission.submitted_by,
            status='pending'
        ).first()
        
        return Response({'status': 'submission approved', 'next_task': TaskSerializer(next_task).data if next_task else None})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        submission = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        submission.status = 'reviewed'
        submission.remarks = request.data.get('remarks', '')
        submission.save()
        
        return Response({'status': 'submission rejected'})

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        exam = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        results = Result.objects.filter(exam=exam).select_related('user')
        data = [{
            'user': result.user.get_full_name() or result.user.username,
            'score': result.score,
            'passed': result.passed,
            'taken_at': result.taken_at
        } for result in results]

        return Response(data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start_exam(self, request):
        """Create a timed attempt and return randomized questions."""
        if request.user.is_staff:
            return Response({'error': 'Staff users cannot take exams.'}, status=status.HTTP_403_FORBIDDEN)

        exam_id = request.data.get('exam_id')
        if not exam_id:
            return Response({'error': 'exam_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)

        # Enforce assignment: if exam is assigned to someone, only they can start it
        if exam.assigned_to_id and exam.assigned_to_id != request.user.id:
            return Response({'error': 'This exam is not assigned to you.'}, status=status.HTTP_403_FORBIDDEN)

        now = timezone.now()

        # If there is an active attempt, either resume it or expire it
        active = ExamAttempt.objects.filter(user=request.user, exam=exam, status='in_progress').order_by('-started_at').first()
        if active:
            if now > active.expires_at:
                active.status = 'expired'
                active.submitted_at = now
                active.save(update_fields=['status', 'submitted_at'])
            else:
                question_ids = list(active.question_order or [])
                questions_qs = Question.objects.filter(exam=exam, id__in=question_ids)
                questions_by_id = {q.id: q for q in questions_qs}
                questions_payload = []
                for qid in question_ids:
                    q = questions_by_id.get(qid)
                    if not q:
                        continue
                    questions_payload.append({
                        'id': q.id,
                        'question_text': q.question_text,
                        'question_type': q.question_type,
                        'options': list(q.options or []),
                    })

                return Response({
                    'attempt_id': active.id,
                    'attempt_number': active.attempt_number,
                    'expires_at': active.expires_at.isoformat(),
                    'duration_seconds': int(max(0, (active.expires_at - now).total_seconds())),
                    'max_attempts': int(exam.max_attempts or 0),
                    'questions': questions_payload,
                })

        completed_attempts = ExamAttempt.objects.filter(
            user=request.user,
            exam=exam,
            status__in=['completed', 'expired']
        ).count()

        max_attempts = int(exam.max_attempts or 0)
        if max_attempts > 0 and completed_attempts >= max_attempts:
            return Response({'error': 'Retake limit reached for this exam.'}, status=status.HTTP_403_FORBIDDEN)

        attempt_number = completed_attempts + 1
        expires_at = now + timedelta(minutes=int(exam.duration_minutes or 0))

        # Randomize questions (and options) per attempt
        questions_qs = Question.objects.filter(exam=exam)
        question_ids = list(questions_qs.values_list('id', flat=True))
        if not question_ids:
            return Response({'error': 'No questions found for this exam'}, status=status.HTTP_400_BAD_REQUEST)

        import random
        random.shuffle(question_ids)

        questions_by_id = {q.id: q for q in questions_qs}
        questions_payload = []
        for qid in question_ids:
            q = questions_by_id.get(qid)
            if not q:
                continue

            opts = list(q.options or [])
            # Fix for True/False questions: ensure options exist
            if q.question_type == 'true_false' and not opts:
                opts = ['True', 'False']
            
            if opts:
                random.shuffle(opts)

            questions_payload.append({
                'id': q.id,
                'question_text': q.question_text,
                'question_type': q.question_type,
                'options': opts,
            })

        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = (request.META.get('HTTP_USER_AGENT') or '')[:1000]

        attempt = ExamAttempt.objects.create(
            user=request.user,
            exam=exam,
            attempt_number=attempt_number,
            expires_at=expires_at,
            question_order=question_ids,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return Response({
            'attempt_id': attempt.id,
            'attempt_number': attempt.attempt_number,
            'expires_at': expires_at.isoformat(),
            'duration_seconds': int((expires_at - now).total_seconds()),
            'max_attempts': max_attempts,
            'questions': questions_payload,
        })

    @action(detail=False, methods=['post'])
    def submit_exam(self, request):
        if request.user.is_staff:
            return Response({'error': 'Staff users cannot submit exams.'}, status=status.HTTP_403_FORBIDDEN)

        attempt_id = request.data.get('attempt_id')
        answers = request.data.get('answers') or {}
        if not attempt_id:
            return Response({'error': 'attempt_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attempt = ExamAttempt.objects.select_related('exam').get(id=attempt_id, user=request.user)
        except ExamAttempt.DoesNotExist:
            return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)

        if attempt.status != 'in_progress':
            return Response({'error': 'This attempt is already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        exam = attempt.exam
        now = timezone.now()
        is_expired = now > attempt.expires_at

        # Normalize answers: accept either {"q123": "A"} or {"123": "A"}
        normalized = {}
        if isinstance(answers, dict):
            for k, v in answers.items():
                key = str(k).strip()
                if key.startswith('q'):
                    key = key[1:]
                if key.isdigit():
                    normalized[int(key)] = str(v).strip()

        question_ids = list(attempt.question_order or [])
        questions = list(Question.objects.filter(exam=exam, id__in=question_ids))
        questions_by_id = {q.id: q for q in questions}

        total_questions = len(question_ids) if question_ids else len(questions)
        if total_questions <= 0:
            return Response({'error': 'No questions found for this exam'}, status=status.HTTP_400_BAD_REQUEST)

        points_per_question = 100 / total_questions
        score = 0.0

        # Score in the presented question order for consistency
        for qid in question_ids:
            q = questions_by_id.get(qid)
            if not q:
                continue
            user_answer = normalized.get(q.id)
            if user_answer is None:
                continue
            if str(user_answer).strip() == str(q.correct_answer).strip():
                score += points_per_question

        score = round(score, 2)
        passed = score >= float(exam.pass_score)

        attempt.answers = {str(k): v for k, v in normalized.items()}
        attempt.score = score
        attempt.passed = passed
        attempt.submitted_at = now
        attempt.status = 'expired' if is_expired else 'completed'
        attempt.save(update_fields=['answers', 'score', 'passed', 'submitted_at', 'status'])

        # Keep Result as the latest-attempt summary for compatibility with existing pages
        result, created = Result.objects.get_or_create(
            user=request.user,
            exam=exam,
            defaults={'score': score, 'passed': passed}
        )
        if not created:
            result.score = score
            result.passed = passed
            result.taken_at = now
            result.save(update_fields=['score', 'passed', 'taken_at'])

        # Auto-generate Certificate if passed
        if passed:
            # Check if certificate already exists to avoid duplicates
            if not Certificate.objects.filter(user=request.user, exam=exam).exists():
                import uuid
                cert_number = f"CERT-{uuid.uuid4().hex[:10].upper()}"
                Certificate.objects.create(
                    user=request.user,
                    exam=exam,
                    certificate_number=cert_number,
                    name=request.user.get_full_name() or request.user.username,
                    institution='TaskCert Platform',
                    score=score
                )

        return Response({
            'score': score,
            'passed': passed,
            'status': attempt.status,
            'attempt_number': attempt.attempt_number,
            'message': 'Exam submitted successfully'
        })

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download certificate as PDF"""
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
        from reportlab.lib.enums import TA_CENTER
        from io import BytesIO
        import os
        
        certificate = self.get_object()
        if certificate.user != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add spacing
        story.append(Spacer(1, 1.5*inch))
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=48,
            textColor='#8B4513',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("Certificate of Completion", title_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Body text
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        story.append(Paragraph("This is to certify that", body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Name
        name_style = ParagraphStyle(
            'CustomName',
            parent=styles['Heading2'],
            fontSize=24,
            textColor='#8B4513',
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        name = certificate.name or certificate.user.get_full_name() or certificate.user.username
        story.append(Paragraph(name, name_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Body text
        story.append(Paragraph("has successfully completed the examination", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Exam/Task name
        exam_style = ParagraphStyle(
            'CustomExam',
            parent=styles['Heading3'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        cert_name = "Unknown Certification"
        if certificate.exam:
            cert_name = certificate.exam.name
        elif certificate.task:
            cert_name = certificate.task.name
            
        story.append(Paragraph(f"<b>{cert_name}</b>", exam_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Institution
        if certificate.institution:
            story.append(Paragraph(f"from <b>{certificate.institution}</b>", body_style))
            story.append(Spacer(1, 0.1*inch))
        
        # Score
        if certificate.score is not None:
            score_formatted = int(round(certificate.score))
            story.append(Paragraph(f"with a score of <b>{score_formatted}%</b>", body_style))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("In recognition of the achievement and competency demonstrated", body_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Certificate details
        details_style = ParagraphStyle(
            'CustomDetails',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor='#666666'
        )
        story.append(Paragraph(f"Certificate No.: {certificate.certificate_number}", details_style))
        story.append(Paragraph(f"Issued: {certificate.issued_date.strftime('%B %d, %Y')}", details_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Return as attachment
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Certificate_{certificate.certificate_number}.pdf"'
        return response


# Template Views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_http_methods


def _is_platform_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    # "Special access members" live in this group
    return user.is_staff and user.groups.filter(name='Platform Admin').exists()

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        if _is_platform_admin(request.user):
            return redirect('/admin-dashboard/')
        if request.user.is_staff:
            return redirect('/mentor-dashboard/')
        return redirect('/dashboard/')

    role = (request.POST.get('role') or request.GET.get('role') or 'student').strip().lower()
    if role not in {'student', 'admin'}:
        role = 'student'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Role-based access control
                if role == 'admin':
                    if not user.is_staff:
                        messages.error(request, 'Access Denied: This portal is for Admins and Mentors only.')
                        return render(request, 'registration/login.html', {'login_role': role})
                elif role == 'student':
                    if user.is_staff:
                        messages.error(request, 'Access Denied: Please use the Admin/Mentor access portal.')
                        return render(request, 'registration/login.html', {'login_role': role})

                from django.contrib.auth import login
                login(request, user)
                
                # Log Activity
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                    
                UserActivityLog.objects.create(
                    user=user,
                    activity_type='login',
                    ip_address=ip,
                    details=f'Web Login as {role}'
                )
                
                # Redirect admins/mentors to appropriate dashboard
                if _is_platform_admin(user):
                    return redirect('/admin-dashboard/')
                if user.is_staff:
                    return redirect('/mentor-dashboard/')
                
                # Verify student has tasks assigned
                if not user.is_staff and not user.is_superuser:
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('/dashboard/')
                    
                return redirect('/dashboard/')
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login.html', {'login_role': role})

@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = (request.POST.get('password') or '').strip()
        password_confirm = (request.POST.get('password_confirm') or '').strip()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        
        if password != password_confirm:
            return render(request, 'registration/register.html', {'error': 'Passwords do not match'})
        
        if not username:
            username = _generate_unique_username(first_name, last_name)
        else:
            cleaned = slugify(username).replace('-', '')
            username = cleaned or _generate_unique_username(first_name, last_name)
            if User.objects.filter(username=username).exists():
                return render(request, 'registration/register.html', {'error': 'Username already exists'})

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='user'
            )
        except IntegrityError:
            # Extremely unlikely race: generate a new username and retry once.
            username = _generate_unique_username(first_name, last_name)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='user'
            )
        # Mentor is assigned by admin/staff later.
        
        from django.contrib.auth import login
        login(request, user)
        return redirect('/dashboard/')
    
    return render(request, 'registration/register.html')


@csrf_protect
def mentor_register_view(request):
    # Only admins/mentors (staff users) can create mentor accounts.
    if not request.user.is_authenticated:
        return redirect('/admin-login/')
    if not request.user.is_staff:
        return redirect('/dashboard/')

    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or '').strip()
        specialization = (request.POST.get('specialization') or '').strip()
        bio = (request.POST.get('bio') or '').strip()

        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        password_confirm = request.POST.get('password_confirm') or ''

        if not full_name:
            return render(request, 'registration/mentor_register.html', {'error': 'Full name is required'})

        if not username:
            return render(request, 'registration/mentor_register.html', {'error': 'Username is required'})

        if not email:
            return render(request, 'registration/mentor_register.html', {'error': 'Email is required'})

        if password != password_confirm:
            return render(request, 'registration/mentor_register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'registration/mentor_register.html', {'error': 'Username already exists'})

        if Mentor.objects.filter(email=email).exists():
            return render(request, 'registration/mentor_register.html', {'error': 'A mentor with this email already exists'})

        try:
            with transaction.atomic():
                mentor = Mentor.objects.create(
                    name=full_name,
                    email=email,
                    bio=bio,
                    specialization=specialization,
                )

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=full_name.split(' ')[0] if full_name else '',
                    last_name=' '.join(full_name.split(' ')[1:]) if full_name and len(full_name.split(' ')) > 1 else '',
                    role='admin',
                    is_staff=True,
                    is_superuser=False,
                )
                user.mentor = mentor
                user.save()
                mentor.user = user
                mentor.save(update_fields=['user'])
        except IntegrityError:
            return render(request, 'registration/mentor_register.html', {'error': 'Could not create mentor account. Please try a different username/email.'})

        messages.success(request, 'Mentor account created successfully.')
        return redirect('/manage-users/')

    return render(request, 'registration/mentor_register.html')

@login_required(login_url='/login/')
def dashboard_view(request):
    # If user is platform admin, redirect to admin dashboard
    if _is_platform_admin(request.user):
        return redirect('/admin-dashboard/')
    # If user is mentor/staff (but not platform admin), redirect to mentor dashboard
    if request.user.is_staff:
        return redirect('/mentor-dashboard/')
    
    # Show ALL active tasks (pending or in_progress) so students always see what is assigned
    current_tasks = Task.objects.filter(
        assigned_to=request.user, 
        status__in=['pending', 'in_progress']
    ).order_by('due_date', 'created_at')

    completed_tasks = Task.objects.filter(assigned_to=request.user, status='completed')
    recent_submissions = Submission.objects.filter(submitted_by=request.user).order_by('-submitted_at')[:5]
    overdue_tasks = Task.objects.filter(assigned_to=request.user, due_date__lt=timezone.now(), status__in=['pending', 'in_progress'])

    total_tasks = Task.objects.filter(assigned_to=request.user).count()
    overall_progress = (completed_tasks.count() / total_tasks * 100) if total_tasks > 0 else 0

    context = {
        'current_tasks': current_tasks,
        'recent_submissions': recent_submissions,
        'overdue_tasks': overdue_tasks,
        'active_tasks_count': current_tasks.count(),
        'completed_tasks_count': completed_tasks.count(),
        'pending_submissions_count': Submission.objects.filter(submitted_by=request.user, status='submitted').count(),
        'certificates_count': Certificate.objects.filter(user=request.user).count(),
        'overall_progress': int(overall_progress),
        'mentor': request.user.mentor,
    }

    return render(request, 'tasks/dashboard.html', context)

@login_required(login_url='/login/')
def exams_view(request):
    # Exams are only for regular users, not staff/admin
    if request.user.is_staff:
        return redirect('/mentor-dashboard/')
    
    # Allow all assigned exams or public exams to be visible
    from django.db.models import Q
    exams = Exam.objects.filter(Q(assigned_to__isnull=True) | Q(assigned_to=request.user))

    attempt_counts = {}
    recent_attempts = []
    if exams.exists():
        from django.db.models import Count
        attempts_qs = ExamAttempt.objects.filter(user=request.user, exam__in=exams).select_related('exam').order_by('-started_at')
        for row in attempts_qs.values('exam_id').annotate(cnt=Count('id')):
            attempt_counts[row['exam_id']] = row['cnt']
        recent_attempts = list(attempts_qs[:10])

    context = {
        'exams': exams,
        'has_completed_all_tasks': True, # Always show exam section
        'attempt_counts': attempt_counts,
        'recent_attempts': recent_attempts,
    }
    return render(request, 'exams/exams.html', context)

@login_required(login_url='/login/')
def certificates_view(request):
    # Only show user's own certificates
    if request.user.is_staff:
        # Admin can see all certificates from manage page
        return redirect('/manage-certificates/')
    
    certificates = Certificate.objects.filter(user=request.user).select_related('exam', 'user')
    
    # Attach the actual exam result score to each certificate
    for cert in certificates:
        result = Result.objects.filter(user=request.user, exam=cert.exam).first()
        cert.exam_result_score = result.score if result else cert.score
    
    context = {
        'certificates': certificates,
    }
    return render(request, 'certificates/certificates.html', context)


@csrf_protect
def verify_certificate_view(request):
    query = (request.POST.get('certificate_number') or request.GET.get('q') or '').strip()
    certificate = None
    error = None

    if query:
        certificate = Certificate.objects.filter(certificate_number__iexact=query).select_related('user', 'exam').first()
        if not certificate:
            error = 'Certificate not found. Please check the certificate number.'

    context = {
        'query': query,
        'certificate': certificate,
        'error': error,
    }
    return render(request, 'certificates/verify_certificate.html', context)

@login_required(login_url='/login/')
def my_tasks_view(request):
    # Show ALL active tasks (pending or in_progress)
    current_tasks = Task.objects.filter(
        assigned_to=request.user, 
        status__in=['pending', 'in_progress']
    ).order_by('due_date', 'created_at')

    completed_tasks = Task.objects.filter(assigned_to=request.user, status='completed')

    context = {
        'current_tasks': current_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'tasks/my_tasks.html', context)

@login_required(login_url='/login/')
def submissions_view(request):
    submissions = Submission.objects.filter(submitted_by=request.user).order_by('-submitted_at')
    
    context = {
        'submissions': submissions,
    }
    return render(request, 'tasks/submissions.html', context)

@login_required(login_url='/login/')
def admin_dashboard_view(request):
    if not _is_platform_admin(request.user):
        return redirect('/mentor-dashboard/' if request.user.is_staff else '/dashboard/')
    
    total_users = User.objects.filter(role='user').count()
    total_tasks = Task.objects.count()
    pending_submissions = Submission.objects.filter(status='submitted').count()
    total_exams = Exam.objects.count()
    
    context = {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'pending_submissions': pending_submissions,
        'total_exams': total_exams,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required(login_url='/login/')
def manage_users_view(request):
    if not _is_platform_admin(request.user):
        return redirect('/mentor-dashboard/' if request.user.is_staff else '/dashboard/')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        mentor_id = (request.POST.get('mentor_id') or '').strip()

        try:
            target_user = User.objects.get(id=user_id, role='user')
        except (User.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'User not found.')
            return redirect('manage_users')

        if mentor_id in {'', 'none', '0'}:
            target_user.mentor = None
            target_user.save(update_fields=['mentor'])
            messages.success(request, f"Mentor unassigned for {target_user.username}.")
            return redirect('manage_users')

        try:
            mentor = Mentor.objects.get(id=mentor_id)
        except (Mentor.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Mentor not found.')
            return redirect('manage_users')

        target_user.mentor = mentor
        target_user.save(update_fields=['mentor'])
        messages.success(request, f"Mentor assigned to {target_user.username}.")
        return redirect('manage_users')

    users = User.objects.filter(role='user')
    mentors = Mentor.objects.all().order_by('name')

    # Calculate statistics
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    mentors_count = Mentor.objects.count()
    # Users joined in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = users.filter(date_joined__gte=thirty_days_ago).count()

    context = {
        'users': users,
        'mentors': mentors,
        'total_users': total_users,
        'active_users': active_users,
        'mentors_count': mentors_count,
        'recent_users': recent_users,
    }
    return render(request, 'admin/manage_users.html', context)

@login_required(login_url='/login/')
def manage_tasks_view(request):
    # Allow if user is staff or is a mentor
    is_mentor = Mentor.objects.filter(id=request.user.id).exists() if request.user.id else False
    
    if not request.user.is_staff and not is_mentor:
        return redirect('/dashboard/')

    tasks = Task.objects.all()

    # Calculate statistics
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()

    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'admin/manage_tasks.html', context)

@login_required(login_url='/login/')
def manage_submissions_view(request):
    if not request.user.is_staff:
        return redirect('/dashboard/')

    submissions = Submission.objects.all().order_by('-submitted_at')

    # Calculate statistics
    total_submissions = submissions.count()
    pending_reviews = submissions.filter(status='submitted').count()
    approved_count = submissions.filter(status='approved').count()
    # Calculate average score for approved submissions
    approved_scores = submissions.filter(status='approved', score__isnull=False).values_list('score', flat=True)
    avg_score = sum(approved_scores) / len(approved_scores) if approved_scores else 0

    context = {
        'submissions': submissions,
        'total_submissions': total_submissions,
        'pending_reviews': pending_reviews,
        'approved_count': approved_count,
        'avg_score': avg_score,
    }
    return render(request, 'admin/manage_submissions.html', context)

@login_required(login_url='/login/')
def manage_exams_view(request):
    if not request.user.is_staff:
        return redirect('/dashboard/')

    exams = Exam.objects.all()
    # Get all exam results
    results = Result.objects.all().select_related('user', 'exam').order_by('-taken_at')

    # Calculate statistics
    total_exams = exams.count()
    total_results = results.count()
    passed_count = results.filter(passed=True).count()
    # Calculate average score
    scores = results.values_list('score', flat=True)
    avg_score = sum(scores) / len(scores) if scores else 0

    context = {
        'exams': exams,
        'results': results,
        'total_exams': total_exams,
        'total_results': total_results,
        'passed_count': passed_count,
        'avg_score': avg_score,
    }
    return render(request, 'admin/manage_exams.html', context)

@login_required(login_url='/login/')
@csrf_protect
def profile_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        return render(request, 'users/profile.html', {
            'success': 'Profile updated successfully!',
            'user': request.user
        })
    
    context = {
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)

@login_required(login_url='/login/')
@csrf_protect
def submit_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.assigned_to != request.user:
        return redirect('/my-tasks/')
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        submitted_file = request.FILES.get('file')
        
        if (not content or content.strip() == '') and not submitted_file:
            return render(request, 'tasks/submit_task.html', {
                'task': task,
                'error': 'Please provide either text submission or upload a file.'
            })
        
        # Check if task is overdue
        if timezone.now() > task.due_date:
            return render(request, 'tasks/submit_task.html', {
                'task': task,
                'error': f'This task is overdue! Due date was {task.due_date.strftime("%B %d, %Y at %I:%M %p")}. Please contact your mentor.'
            })
        
        # Create submission
        submission = Submission.objects.create(
            task=task,
            submitted_by=request.user,
            content=content,
            file=submitted_file,
            status='submitted'
        )
        
        # Update task status
        task.status = 'in_progress'
        task.save()
        
        return render(request, 'tasks/submit_task.html', {
            'task': task,
            'success': f'Your work for "{task.name}" has been submitted successfully! It will be reviewed by an admin.'
        })
    
    context = {
        'task': task,
        'is_overdue': timezone.now() > task.due_date,
    }
    return render(request, 'tasks/submit_task.html', context)

@login_required(login_url='/login/')
@csrf_protect
def review_submission_view(request, submission_id):
    if not request.user.is_staff:
        return redirect('/dashboard/')
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        score = request.POST.get('score', None)
        
        submission.remarks = remarks
        
        if action == 'approve':
            submission.status = 'approved'
            submission.score = float(score) if score else 100
            submission.save()
            
            # Mark task as completed
            submission.task.status = 'completed'
            submission.task.save()
            
            # Generate Certificate for the Task
            if not Certificate.objects.filter(user=submission.submitted_by, task=submission.task).exists():
                import uuid
                cert_number = f"TASK-{uuid.uuid4().hex[:10].upper()}"
                Certificate.objects.create(
                    user=submission.submitted_by,
                    task=submission.task,
                    certificate_number=cert_number,
                    name=submission.submitted_by.get_full_name() or submission.submitted_by.username,
                    institution='TaskCert Platform',
                    score=submission.score
                )
                
                # Log Activity
                try:
                    UserActivityLog.objects.create(
                        user=submission.submitted_by,
                        activity_type='certificate_issued',
                        details=f'Certificate issued for Task: {submission.task.name}'
                    )
                except Exception:
                    pass

            # Auto-assign next task if available
            user_tasks = Task.objects.filter(
                assigned_to=submission.submitted_by,
                status__in=['pending', 'in_progress']
            ).order_by('created_at')
            
            if user_tasks.exists():
                next_task = user_tasks.first()
                next_task.status = 'pending'
                next_task.save()
                
                return render(request, 'admin/review_submission.html', {
                    'submission': submission,
                    'success': f'Submission approved! Next task "{next_task.name}" has been assigned to {submission.submitted_by.username}.'
                })
            else:
                return render(request, 'admin/review_submission.html', {
                    'submission': submission,
                    'success': f'Submission approved! All tasks completed for {submission.submitted_by.username}. Congratulations!'
                })
        
        elif action == 'reject':
            submission.status = 'submitted'
            submission.save()
            
            return render(request, 'admin/review_submission.html', {
                'submission': submission,
                'success': f'Submission sent back to {submission.submitted_by.username} with remarks. They have been notified to resubmit.'
            })
    
    context = {
        'submission': submission,
    }
    return render(request, 'admin/review_submission.html', context)

@login_required(login_url='/login/')
@csrf_protect
def assign_tasks_view(request):
    # Check if user is a mentor or admin
    user_mentor = getattr(request.user, 'mentor', None) if hasattr(request.user, 'mentor') else None
    
    # Allow if user is staff (admin) or is a mentor
    is_mentor = Mentor.objects.filter(id=request.user.id).exists() if request.user.id else False
    
    if not request.user.is_staff and not is_mentor:
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        task_name = request.POST.get('name', '')
        task_description = request.POST.get('remarks', '')
        due_date = request.POST.get('due_date', '')
        # Get list of selected users
        user_ids = request.POST.getlist('assigned_to')
        
        if not all([task_name, due_date]) or not user_ids:
            return render(request, 'mentor/assign_tasks.html', {
                'error': 'Please fill in all required fields and select at least one user.',
                'users': User.objects.filter(role='user')
            })
            
        # Validate due date
        try:
            # Assuming format from datetime-local input is YYYY-MM-DDTHH:MM
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
            if timezone.make_aware(due_date_obj) < timezone.now():
                return render(request, 'mentor/assign_tasks.html', {
                    'error': 'Due date cannot be in the past.',
                    'users': User.objects.filter(role='user')
                })
        except ValueError:
            # Fallback if format is different or parsing fails
            pass
        
        # Use the logged-in user as mentor if they're an admin, otherwise use their mentor relationship
        if request.user.is_staff:
            mentor = Mentor.objects.first()  # Get any mentor for admin
        else:
            mentor = Mentor.objects.filter(users=request.user).first() or Mentor.objects.first()
            
        success_count = 0
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id, role='user')
                
                Task.objects.create(
                    name=task_name,
                    remarks=task_description,
                    due_date=due_date,
                    assigned_to=user,
                    assigned_by=mentor,
                    status='pending'
                )
                success_count += 1
            except User.DoesNotExist:
                continue
                
        if success_count > 0:
            return render(request, 'mentor/assign_tasks.html', {
                'success': f'Task "{task_name}" has been successfully assigned to {success_count} student(s)!',
                'users': User.objects.filter(role='user')
            })
        else:
             return render(request, 'mentor/assign_tasks.html', {
                'error': 'No valid users selected or error processing assignment.',
                'users': User.objects.filter(role='user')
            })

    
    if _is_platform_admin(request.user):
        users = User.objects.filter(role='user')
    else:
        mentor_profile = getattr(request.user, 'mentor_profile', None)
        if mentor_profile:
            users = User.objects.filter(role='user', mentor=mentor_profile)
        else:
            users = User.objects.none()
    context = {
        'users': users,
    }
    return render(request, 'mentor/assign_tasks.html', context)

@login_required(login_url='/login/')
def mentor_dashboard_view(request):
    # Check if user is a mentor or admin
    if not request.user.is_staff:
        return redirect('/dashboard/')

    if request.user.is_superuser:
        return redirect('/admin-dashboard/')
    
    # Get all tasks created by mentors
    all_tasks = Task.objects.all().order_by('-created_at')
    
    # Get pending submissions
    pending_submissions = Submission.objects.filter(status='submitted').count()
    
    # Get stats
    # Get stats
    mentor_profile = getattr(request.user, 'mentor_profile', None)
    if mentor_profile:
        total_users = User.objects.filter(role='user', mentor=mentor_profile).count()
    else:
        total_users = 0
    completed_tasks = Task.objects.filter(status='completed').count()
    
    context = {
        'all_tasks': all_tasks[:10],
        'pending_submissions': pending_submissions,
        'total_users': total_users,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'mentor/dashboard.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        # Log Activity
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
                
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='logout',
                ip_address=ip,
                details='Web Logout'
            )
        except Exception:
            pass
            
    auth_logout(request)
    return redirect('/login/')

@login_required(login_url='/login/')
@csrf_protect
def manage_certificates_view(request):
    if not request.user.is_staff:
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            result_id = request.POST.get('result_id')
            institution_name = request.POST.get('institution_name', '')
            
            try:
                result = Result.objects.get(id=result_id)
                if not result.passed:
                    # Get all passed results without certificates
                    passed_results = Result.objects.filter(passed=True).select_related('user', 'exam')
                    pending = []
                    for r in passed_results:
                        if not Certificate.objects.filter(user=r.user, exam=r.exam).exists():
                            pending.append(r)
                    
                    return render(request, 'admin/manage_certificates.html', {
                        'error': 'Can only create certificates for passed exams',
                        'certificates': Certificate.objects.all().order_by('-issued_date'),
                        'pending_results': pending,
                    })
                
                # Check if certificate already exists
                if Certificate.objects.filter(user=result.user, exam=result.exam).exists():
                    # Get all passed results without certificates
                    passed_results = Result.objects.filter(passed=True).select_related('user', 'exam')
                    pending = []
                    for r in passed_results:
                        if not Certificate.objects.filter(user=r.user, exam=r.exam).exists():
                            pending.append(r)
                    
                    return render(request, 'admin/manage_certificates.html', {
                        'error': 'Certificate already exists for this exam',
                        'certificates': Certificate.objects.all().order_by('-issued_date'),
                        'pending_results': pending,
                    })
                
                import uuid
                cert_number = f"CERT-{uuid.uuid4().hex[:10].upper()}"
                
                certificate = Certificate.objects.create(
                    user=result.user,
                    exam=result.exam,
                    certificate_number=cert_number,
                    name=result.user.get_full_name() or result.user.username,
                    institution=institution_name,
                    score=result.score
                )
                
                # Get all passed results without certificates
                passed_results = Result.objects.filter(passed=True).select_related('user', 'exam')
                pending = []
                for r in passed_results:
                    if not Certificate.objects.filter(user=r.user, exam=r.exam).exists():
                        pending.append(r)
                
                return render(request, 'admin/manage_certificates.html', {
                    'success': f'Certificate {cert_number} created successfully for {result.user.username}',
                    'certificates': Certificate.objects.all().order_by('-issued_date'),
                    'pending_results': pending,
                })
            except Result.DoesNotExist:
                # Get all passed results without certificates
                passed_results = Result.objects.filter(passed=True).select_related('user', 'exam')
                pending = []
                for r in passed_results:
                    if not Certificate.objects.filter(user=r.user, exam=r.exam).exists():
                        pending.append(r)
                
                return render(request, 'admin/manage_certificates.html', {
                    'error': 'Result not found',
                    'certificates': Certificate.objects.all().order_by('-issued_date'),
                    'pending_results': pending,
                })
    
    # Get certificates and pending results
    certificates = Certificate.objects.all().order_by('-issued_date')

    # Get all passed results without certificates
    passed_results = Result.objects.filter(passed=True).select_related('user', 'exam')
    pending_results = []
    for result in passed_results:
        if not Certificate.objects.filter(user=result.user, exam=result.exam).exists():
            pending_results.append(result)

    # Calculate statistics
    total_certificates = certificates.count()
    pending_certificates = len(pending_results)
    # Certificates issued today
    today = timezone.now().date()
    issued_today = certificates.filter(issued_date__date=today).count()
    # Calculate average score
    scores = certificates.values_list('score', flat=True)
    avg_score = sum(scores) / len(scores) if scores else 0

    context = {
        'certificates': certificates,
        'pending_results': pending_results,
        'total_certificates': total_certificates,
        'pending_certificates': pending_certificates,
        'issued_today': issued_today,
        'avg_score': avg_score,
    }
    return render(request, 'admin/manage_certificates.html', context)

@login_required(login_url='/login/')
def sample_questions_topics_view(request):
    """View for selecting a topic to view sample questions"""
    topics = Topic.objects.filter(is_active=True).order_by('name')

    # Add question counts to each topic for template use
    for topic in topics:
        topic.total_questions = topic.sample_questions.count()
        topic.active_questions = topic.sample_questions.filter(is_active=True).count()

    context = {
        'topics': topics,
    }
    return render(request, 'sample_questions/topics.html', context)

@login_required(login_url='/login/')
def sample_questions_view(request, topic_id):
    """View for displaying sample questions for a specific topic"""
    topic = get_object_or_404(Topic, id=topic_id, is_active=True)
    questions = SampleQuestion.objects.filter(topic=topic, is_active=True).order_by('difficulty_level', '-created_at')

    context = {
        'topic': topic,
        'questions': questions,
    }
    return render(request, 'sample_questions/questions.html', context)


@login_required(login_url='/login/')
@csrf_protect
def create_exam_view(request):
    if not request.user.is_staff:
        return redirect('/dashboard/')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        duration = request.POST.get('duration_minutes', 30)
        pass_score = request.POST.get('pass_score', 60)
        max_attempts = request.POST.get('max_attempts', 3)
        assigned_to_id = request.POST.get('assigned_to')

        if not name:
             return render(request, 'admin/create_exam.html', {'error': 'Exam name is required', 'users': User.objects.filter(role='user')})

        # Get mentor for created_by
        mentor = getattr(request.user, 'mentor_profile', None)
        if not mentor:
            # Fallback if staff user isn't linked to a mentor profile properly
            mentor = Mentor.objects.first()

        assigned_user = None
        if assigned_to_id:
            assigned_user = User.objects.filter(id=assigned_to_id).first()

        exam = Exam.objects.create(
            name=name,
            description=description,
            duration_minutes=int(duration),
            pass_score=float(pass_score),
            max_attempts=int(max_attempts),
            created_by=mentor,
            assigned_to=assigned_user
        )
        
        return redirect(f'/manage-exams/{exam.id}/add-questions/')

    # Get users for assignment dropdown (filtered by mentor)
    if _is_platform_admin(request.user):
        users = User.objects.filter(role='user')
    else:
        mentor = getattr(request.user, 'mentor_profile', None)
        users = User.objects.filter(role='user', mentor=mentor) if mentor else User.objects.none()

    return render(request, 'admin/create_exam.html', {'users': users})


@login_required(login_url='/login/')
@csrf_protect
def add_questions_view(request, exam_id):
    if not request.user.is_staff:
        return redirect('/dashboard/')

    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        correct_answer = request.POST.get('correct_answer')
        
        options = []
        if question_type == 'multiple_choice':
            op1 = request.POST.get('option_1', '').strip()
            op2 = request.POST.get('option_2', '').strip()
            op3 = request.POST.get('option_3', '').strip()
            op4 = request.POST.get('option_4', '').strip()
            if op1: options.append(op1)
            if op2: options.append(op2)
            if op3: options.append(op3)
            if op4: options.append(op4)
        
        Question.objects.create(
            exam=exam,
            question_text=question_text,
            question_type=question_type,
            options=options if options else None,
            correct_answer=correct_answer
        )
        
        # Re-fetch questions to include the new one
        return render(request, 'admin/add_questions.html', {
            'exam': exam,
            'questions': exam.questions.all().order_by('id'),
            'success': 'Question added successfully!'
        })

    return render(request, 'admin/add_questions.html', {
        'exam': exam,
        'questions': exam.questions.all().order_by('id')
    })

@login_required(login_url='/login/')
def delete_question_view(request, question_id):
    if not request.user.is_staff:
        return redirect('/dashboard/')
    
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.exam.id
    if request.method == 'POST':
        question.delete()
        return redirect(f'/manage-exams/{exam_id}/add-questions/')
    
    return redirect(f'/manage-exams/{exam_id}/add-questions/')

@login_required(login_url='/login/')
@csrf_protect
def edit_exam_view(request, exam_id):
    if not request.user.is_staff:
        return redirect('/dashboard/')
    
    exam = get_object_or_404(Exam, id=exam_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        duration = request.POST.get('duration_minutes', 30)
        pass_score = request.POST.get('pass_score', 60)
        max_attempts = request.POST.get('max_attempts', 3)
        assigned_to_id = request.POST.get('assigned_to')
        
        if not name:
             # Basic validation
             pass 

        assigned_user = None
        if assigned_to_id:
            assigned_user = User.objects.filter(id=assigned_to_id).first()
            
        exam.name = name
        exam.description = description
        exam.duration_minutes = int(duration)
        exam.pass_score = float(pass_score)
        exam.max_attempts = int(max_attempts)
        exam.assigned_to = assigned_user
        exam.save()
        
        messages.success(request, 'Exam updated successfully.')
        return redirect('/manage-exams/')

    # Get users for assignment dropdown
    if _is_platform_admin(request.user):
        users = User.objects.filter(role='user')
    else:
        mentor = getattr(request.user, 'mentor_profile', None)
        users = User.objects.filter(role='user', mentor=mentor) if mentor else User.objects.none()
        
    return render(request, 'admin/edit_exam.html', {'exam': exam, 'users': users})

@login_required(login_url='/login/')
@csrf_protect
def delete_exam_view(request, exam_id):
    if not request.user.is_staff:
        return redirect('/dashboard/')
        
    if request.method == 'POST':
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        messages.success(request, 'Exam deleted successfully.')
        
    return redirect('/manage-exams/')

@login_required(login_url='/login/')
@csrf_protect
def edit_question_view(request, question_id):
    if not request.user.is_staff:
        return redirect('/dashboard/')

    question = get_object_or_404(Question, id=question_id)
    exam = question.exam

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        correct_answer = request.POST.get('correct_answer')
        
        options = []
        if question_type == 'multiple_choice':
            op1 = request.POST.get('option_1', '').strip()
            op2 = request.POST.get('option_2', '').strip()
            op3 = request.POST.get('option_3', '').strip()
            op4 = request.POST.get('option_4', '').strip()
            # Preserve order or layout if needed, but list is simple
            if op1: options.append(op1)
            if op2: options.append(op2)
            if op3: options.append(op3)
            if op4: options.append(op4)
        
        question.question_text = question_text
        question.question_type = question_type
        question.correct_answer = correct_answer
        question.options = options if options else None
        
        # True/False safety
        if question_type == 'true_false' and not question.options:
             question.options = ['True', 'False']
             
        question.save()
        
        messages.success(request, 'Question updated successfully.')
        return redirect(f'/manage-exams/{exam.id}/add-questions/')

    return render(request, 'admin/edit_question.html', {'question': question})
        
    return redirect(f'/manage-exams/{exam_id}/add-questions/')



@login_required(login_url='/login/')
def activity_log_view(request):
    if not _is_platform_admin(request.user):
        return redirect('/dashboard/')
        
    logs = UserActivityLog.objects.all().select_related('user')
    
    # Simple filtering
    user_id = request.GET.get('user')
    date_str = request.GET.get('date')
    
    if user_id:
        logs = logs.filter(user_id=user_id)
    if date_str:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date=date_obj)
        except ValueError:
            pass
            
    users = User.objects.all().order_by('username').only('id', 'username', 'first_name', 'last_name')
    
    return render(request, 'admin/activity_log.html', {
        'logs': logs[:200], # Limit to last 200 for performance/display
        'users': users,
        'selected_user_id': int(user_id) if user_id else None,
        'selected_date': date_str
    })

# ==========================================
# RESOURCE LIBRARY VIEWS
# ==========================================

@login_required(login_url='/login/')
def resource_library_view(request):
    resources = Resource.objects.all().order_by('-created_at')
    return render(request, 'resources/library.html', {'resources': resources})

@login_required(login_url='/login/')
def upload_resource_view(request):
    # Only staff (mentors/admins) can upload
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to upload resources.')
        return redirect('resource_library')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')

        if not title or not file:
            messages.error(request, 'Title and File are required.')
            return redirect('upload_resource')

        try:
            Resource.objects.create(
                title=title,
                description=description,
                file=file,
                uploaded_by=request.user
            )
            messages.success(request, 'Resource uploaded successfully!')
            return redirect('resource_library')
        except Exception as e:
            messages.error(request, f'Error uploading resource: {str(e)}')
            return redirect('upload_resource')

    return render(request, 'resources/upload_resource.html')


# ==========================================
# COMMUNITY FORUM VIEWS
# ==========================================

@login_required(login_url='/login/')
def forum_index_view(request):
    posts = ForumPost.objects.all().order_by('-created_at')
    return render(request, 'forum/index.html', {'posts': posts})

@login_required(login_url='/login/')
def create_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title and content:
            post = ForumPost.objects.create(
                title=title,
                content=content,
                author=request.user
            )
            messages.success(request, 'Discussion started successfully!')
            return redirect('forum_index')
        else:
            messages.error(request, 'Title and content are required.')
            
    return render(request, 'forum/create_post.html')

@login_required(login_url='/login/')
def post_detail_view(request, post_id):
    from django.shortcuts import get_object_or_404
    post = get_object_or_404(ForumPost, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ForumComment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            messages.success(request, 'Comment posted!')
            return redirect('post_detail', post_id=post.id)
        else:
            messages.error(request, 'Comment cannot be empty.')
            
    return render(request, 'forum/post_detail.html', {'post': post})

