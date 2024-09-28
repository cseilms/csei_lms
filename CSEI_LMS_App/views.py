import pandas as pd
import os
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
import requests

from .models import Result, Department, CourseModules, AccommodationApplication, Enquiry, Essay_Exam_Db, Essay_StudentAnswer, \
    Essay_Result, CourseStudent
from .forms import ApplicationForm, AccommodationApplicationForm, EnquiryForm, CourseForm
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponseForbidden

from CSEI_LMS_Project import settings
from .models import (BatchStudent, BatchFile, DailyTopic, DailyAssignment,
                     AssignmentUpload, Attendance, ContactMessage, ExamDb, Question)
from .forms import (BatchForm, BatchFileForm, DailyTopicForm, DailyAssignmentForm,
                    TeacherRegistrationForm,
                    TeacherLoginForm, ContactForm, AssignmentUploadForm, ExamForm,QuestionForm  )
# essayexam
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import  Batch, TeacherDb  # Make sure to import your models
from .forms import EssayExamForm  # Assuming you have a form for essay exams
from django.views import View

from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta



from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.urls import reverse
from .forms import StudentRegistrationForm
from .models import Student
import logging
# Get a logger instance
logger = logging.getLogger(__name__)



def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            username = student.name.replace(" ", "_")  # Replace spaces in the name for the username
            email = student.email
            password = get_random_string(length=8)

            # Create user with the generated password
            user = User.objects.create_user(username=username, email=email, password=password)
            student.user = user
            student.generated_password = password
            student.save()

            # Send welcome email with the login link
            send_welcome_email(student)

            messages.success(request, 'Registration successful! Please check your email for your login details.')
            return redirect('index')
        else:
            messages.error(request, 'Form is not valid. Please check the errors below.')
    else:
        form = StudentRegistrationForm()

    return render(request, 'student_register.html', {'form': form})


def send_welcome_email(student):
    # Email subject
    email_subject = 'Welcome to CSEI Academy LMS'

    # Generate login link
    login_link = 'http://127.0.0.1:8000/student_login/'

    # Generate HTML message
    html_message = render_to_string('welcome_email.html', {
        'student': student,
        'login_link': login_link
    })

    # Generate plain text message
    plain_message = strip_tags(html_message)

    # Send email
    try:
        send_mail(
            email_subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            html_message=html_message
        )
    except Exception as e:
        logger.error(f"Error sending welcome email to {student.email}: {str(e)}")
def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)

            # Create teacher profile
            teacher = TeacherDb(user=user, **form.cleaned_data)
            teacher.save()

            # Send plain text welcome email
            subject = 'Welcome to CSEI Academy'
            message = (
                f"Dear {teacher.name},\n\n"
                "Welcome to CSEI Academy! Your registration is successful. Below are your details:\n\n"
                f"Name: {teacher.name}\n"
                f"Email: {teacher.user.email}\n"
                f"Designation: {teacher.designation}\n\n"
                "For any inquiries or assistance, please contact us at:\n"
                "Email: support@example.com\n"
                "Phone: 123-456-7890\n\n"
                "Best regards,\n"
                "CSEI Academy Team"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, [teacher.user.email])

            # Flash success message and redirect to login page
            messages.success(request, 'Registration successful! A welcome message has been sent to your email.')
            return redirect('teacher_login')  # Redirect to the login page
        else:
            messages.error(request, 'There was an error with the form. Please correct the errors below.')
    else:
        form = TeacherRegistrationForm()

    return render(request, 'teacher_register.html', {'form': form})



def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    teacher = TeacherDb.objects.get(user=user)
                    if teacher.approved:
                        login(request, user)
                        return redirect('teacher_page')
                    else:
                        messages.error(request, 'Your account is pending approval. Please wait for admin approval.')
                except TeacherDb.DoesNotExist:
                    messages.error(request, 'Your account is not recognized as a teacher.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = TeacherLoginForm()

    return render(request, 'teacher_login.html', {'form': form})

@login_required
def teacher_page(request):
    teacher = get_object_or_404(TeacherDb, user=request.user)
    batches = Batch.objects.filter(teacher=teacher)
    return render(request, 'teacher_page.html', {'teacher': teacher, 'batches': batches})

@login_required
def view_batch_details(request):
    teacher = get_object_or_404(TeacherDb, user=request.user)  # Get the current teacher
    batches = Batch.objects.filter(teacher=teacher)  # Filter batches by the teacher
    return render(request, 'view_batch_details.html', {'batches': batches})


@login_required
def student_page(request, student_id):
    if not hasattr(request.user, 'student'):
        return HttpResponseForbidden("You do not have permission to view this page.")

    student = get_object_or_404(Student, id=student_id)

    if request.user.student != student:
        return HttpResponseForbidden("You do not have permission to view this page.")

    batch_students = BatchStudent.objects.filter(student=student)
    batches = []

    for batch_student in batch_students:
        batch = batch_student.batch
        daily_topics = DailyTopic.objects.filter(batch=batch)
        daily_assignments = DailyAssignment.objects.filter(batch=batch)
        files = BatchFile.objects.filter(batch=batch)
        exams = ExamDb.objects.filter(batch=batch)  # Fetch exams for the batch

        batches.append({
            'batch': batch,
            'daily_topics': daily_topics,
            'daily_assignments': daily_assignments,
            'files': files,
            'exams': exams  # Add exams to the context
        })

    return render(request, 'student_page.html', {'student': student, 'batches': batches})


@login_required
def student_view_exams(request, batch_id):
    # Fetch the batch object
    batch = get_object_or_404(Batch, id=batch_id)

    # Fetch only active exams for the batch
    exams = ExamDb.objects.filter(batch=batch, is_active=True)

    # Get the currently logged-in student (assuming Student model is linked to User model)
    user = request.user
    student = get_object_or_404(Student, user=user)

    context = {
        'batch': batch,
        'exams': exams,
        'student': student,  # Pass the Student object
    }

    return render(request, 'student_view_exams.html', context)
@login_required
def add_batch(request):
    teacher = get_object_or_404(TeacherDb, user=request.user)

    if request.method == 'POST':
        form = BatchForm(request.POST, teacher=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch added successfully.')
            return redirect('teacher_page')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BatchForm(teacher=teacher)
    return render(request, 'add_batch.html', {'form': form})
@login_required
def assign_student_to_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    teacher = get_object_or_404(TeacherDb, user=request.user)
    students = Student.objects.filter(department=teacher.department)
    existing_assignments = BatchStudent.objects.filter(batch=batch).values_list('student_id', flat=True)

    if request.method == 'POST':
        selected_students = request.POST.getlist('students')
        new_students = [student_id for student_id in selected_students if student_id not in existing_assignments]
        new_assignments = [BatchStudent(batch=batch, student_id=student_id) for student_id in new_students]

        if new_assignments:
            BatchStudent.objects.bulk_create(new_assignments)

        return redirect('batch_details', id=batch.id)

    return render(request, 'assign_student_to_batch.html', {
        'batch': batch,
        'students': students,
        'assigned_students': existing_assignments,
    })
@login_required
def add_file_to_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    if request.method == 'POST':
        form = BatchFileForm(request.POST, request.FILES)
        if form.is_valid():
            batch_file = form.save(commit=False)
            batch_file.batch = batch
            batch_file.save()
            messages.success(request, 'File added to batch successfully.')
            return redirect('teacher_view_files', batch_id=batch_id)
    else:
        form = BatchFileForm()

    return render(request, 'add_file_to_batch.html', {'form': form, 'batch': batch})
@login_required
def teacher_view_files(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    files = BatchFile.objects.filter(batch=batch)
    return render(request, 'teacher_files.html', {'batch': batch, 'files': files})


@login_required
def replace_batch_file(request, batch_id, file_id):
    batch = get_object_or_404(Batch, id=batch_id)
    batch_file = get_object_or_404(BatchFile, id=file_id, batch=batch)

    if request.method == 'POST':
        new_file = request.FILES.get('file')
        if new_file:
            batch_file.file = new_file
            batch_file.save()
            messages.success(request, 'File replaced successfully.')
            return redirect('teacher_view_files', batch_id=batch_id)
    return render(request, 'replace_batch_file.html', {'batch': batch, 'file': batch_file})

@login_required
def delete_batch_file(request, batch_id, file_id):
    batch_file = get_object_or_404(BatchFile, id=file_id)

    if request.method == 'POST':
        batch_file.delete()
        messages.success(request, 'File deleted successfully.')
        return redirect('teacher_view_files', batch_id=batch_id)

    return render(request, 'confirm_delete_file.html', {'batch_file': batch_file})


@login_required
def upload_assignment(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    student = request.user.student  # Assuming the user has a related student object

    if request.method == 'POST':
        form = AssignmentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            assignment_upload = form.save(commit=False)
            assignment_upload.student = student
            assignment_upload.batch = batch
            assignment_upload.save()
            messages.success(request, 'Assignment uploaded successfully.')
            return redirect('student_page', student_id=request.user.student.id)  # Redirect here
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AssignmentUploadForm()

    return render(request, 'upload_assignment.html', {'form': form, 'batch': batch, 'student_id': student.id})
@login_required
def add_topic(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    if request.method == 'POST':
        form = DailyTopicForm(request.POST)
        if form.is_valid():
            daily_topic = form.save(commit=False)
            daily_topic.batch = batch
            daily_topic.save()
            messages.success(request, 'Topic added successfully.')
            return redirect('batch_details', id=batch_id)  # Updated parameter name
    else:
        form = DailyTopicForm()

    return render(request, 'add_topic.html', {'form': form, 'batch': batch})
@login_required
def add_assignment(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    if request.method == 'POST':
        form = DailyAssignmentForm(request.POST)
        if form.is_valid():
            daily_assignment = form.save(commit=False)
            daily_assignment.batch = batch
            daily_assignment.save()

            logger.info("Assignment added successfully. Calling notify_students...")

            try:
                # Call the function to notify students
                notify_students(batch, daily_assignment)
                messages.success(request, 'Assignment added and students notified successfully.')
            except Exception as e:
                messages.error(request, f'Assignment added, but there was an error notifying students: {e}')
                logger.error(f"Error notifying students: {str(e)}")

            return redirect('batch_details', id=batch_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DailyAssignmentForm()

    return render(request, 'add_assignment.html', {'form': form, 'batch': batch})
def notify_students(batch, daily_assignment):
    logger.info("Notifying students...")

    try:
        # Get all students related to the batch
        students = batch.batch_students.all()
        logger.debug(f"Batch students: {students}")

        # Extract email addresses
        student_emails = list(students.values_list('student__user__email', flat=True))
        student_emails = list(filter(None, student_emails))  # Filter out any None or empty emails
        logger.debug(f"Student emails: {student_emails}")

        if not student_emails:
            logger.info("No student emails found.")
            return

        subject = 'New Assignment Added'
        message = (
            f'A new assignment has been added to your batch "{batch.name}".\n\n'
            f'Date: {daily_assignment.date}\n'
            f'Assignment: {daily_assignment.assignments}\n\n'
            f'Please check your batch details for more information.'
        )
        from_email = settings.DEFAULT_FROM_EMAIL

        for email in student_emails:
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {email}")
            except Exception as e:
                logger.error(f"Error sending email to {email}: {str(e)}")

    except Exception as e:
        logger.error(f"Error retrieving students or sending emails: {str(e)}")

@login_required
def batch_details(request, id):
    batch = get_object_or_404(Batch, id=id)

    if request.method == 'POST':
        if 'add_topic' in request.POST:
            topic_form = DailyTopicForm(request.POST)
            if topic_form.is_valid():
                topic = topic_form.save(commit=False)
                topic.batch = batch
                topic.save()
                return redirect('batch_details', id=batch.id)
        elif 'add_assignment' in request.POST:
            assignment_form = DailyAssignmentForm(request.POST)
            if assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                assignment.batch = batch
                assignment.save()
                return redirect('batch_details', id=batch.id)
        elif 'add_file' in request.POST:
            file_form = BatchFileForm(request.POST, request.FILES)
            if file_form.is_valid():
                batch_file = file_form.save(commit=False)
                batch_file.batch = batch
                batch_file.save()
                return redirect('batch_details', id=batch.id)
    else:
        topic_form = DailyTopicForm()
        assignment_form = DailyAssignmentForm()
        file_form = BatchFileForm()

    assigned_students = batch.students.all()

    # Fetch daily topics and assignments
    daily_topics = batch.daily_topics.all()
    daily_assignments = batch.daily_assignments.all()
    files = BatchFile.objects.filter(batch=batch)

    # Group topics and assignments by date
    topics_by_date = {}
    assignments_by_date = {}

    for topic in daily_topics:
        topics_by_date.setdefault(topic.date, []).append(topic)

    for assignment in daily_assignments:
        assignments_by_date.setdefault(assignment.date, []).append(assignment)

    return render(request, 'batch_details.html', {
        'batch': batch,
        'assigned_students': assigned_students,
        'topics_by_date': topics_by_date,
        'assignments_by_date': assignments_by_date,
        'topic_form': topic_form,
        'assignment_form': assignment_form,
        'file_form': file_form,
        'files': files,
    })


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def student_view_files(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    files = BatchFile.objects.filter(batch=batch)

    # Retrieve the student_id from the logged-in user
    student_id = request.user.student.id

    return render(request, 'student_files.html', {
        'batch': batch,
        'files': files,
        'student_id': student_id
    })
@login_required
def view_daily_assignment(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    assignments = DailyAssignment.objects.filter(batch=batch)
    return render(request, 'view_daily_assignment.html', {
        'batch': batch,
        'assignments': assignments
    })
@login_required
def view_daily_topic(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    topics = DailyTopic.objects.filter(batch=batch)
    return render(request, 'view_daily_topic.html', {
        'batch': batch,
        'topics': topics
    })
@login_required
def student_batch_details(request, batch_id):
    # Fetch the batch and related data
    batch = get_object_or_404(Batch, id=batch_id)
    daily_topics = batch.daily_topics.all()
    daily_assignments = batch.daily_assignments.all()
    files = batch.files.all()
    student_id = request.user.student.id
    topics_by_date = {}
    assignments_by_date = {}
    for topic in daily_topics:
        topics_by_date.setdefault(topic.date, []).append(topic)
    for assignment in daily_assignments:
        assignments_by_date.setdefault(assignment.date, []).append(assignment)

    context = {
        'batch': batch,
        'daily_topics': daily_topics,
        'daily_assignments': daily_assignments,
        'topics_by_date': topics_by_date,
        'assignments_by_date': assignments_by_date,
        'files': files,
        'student_id': student_id
    }
    return render(request, 'student_batch_details.html', context)


def index(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'teacherdb'):
            # Redirect teachers to their page
            return redirect('teacher_page')
        elif hasattr(request.user, 'student'):
            # Redirect students to their page
            return redirect('student_page', student_id=request.user.student.id)

    teachers = TeacherDb.objects.all()
    return render(request, 'index.html', {'teachers': teachers})

@login_required
def student_assignments(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    assignments = AssignmentUpload.objects.filter(batch=batch)
    print(assignments)
    return render(request, 'students_assignments.html', {'batch': batch, 'assignments': assignments, 'student': request.user})

def attendance_form_view(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    if request.method == 'POST':
        students = request.POST.getlist('students')  # List of selected students
        mark_all_present = request.POST.get('mark_all_present')  # Checkbox for all present
        date_str = request.POST.get('date')

        if not date_str:
            return render(request, 'attendance_form.html',
                          {'batch': batch, 'students': students, 'error': 'Date is required'})

        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'attendance_form.html',
                          {'batch': batch, 'students': students, 'error': 'Invalid date format'})

        # Fetch all students in the batch
        all_students = BatchStudent.objects.filter(batch=batch).values_list('student', flat=True)

        if mark_all_present:
            students_to_mark = all_students
        else:
            students_to_mark = [int(student_id) for student_id in students]

        # Process attendance for all students
        for student_id in all_students:
            student = get_object_or_404(Student, id=student_id)
            is_present_status = student_id in students_to_mark
            process_attendance(batch, student, date, is_present_status)

            # If the student is absent, send a notification
            if not is_present_status:
                send_absence_notification(student)

        return redirect('attendance_view', batch_id=batch.id)

    # Prepare the list of students for the form
    batch_students = BatchStudent.objects.filter(batch=batch)
    students = [batch_student.student for batch_student in batch_students]

    return render(request, 'attendance_form.html', {'batch': batch, 'students': students})
def process_attendance(batch, student, date, is_present):
    Attendance.objects.update_or_create(
        batch=batch,
        student=student,
        date=date,
        defaults={'is_present': is_present}
    )

def attendance_view(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Get the start and end dates for the month
    start_date = timezone.datetime(current_year, current_month, 1).date()
    end_date = (timezone.datetime(current_year, current_month + 1, 1) if current_month < 12
                else timezone.datetime(current_year + 1, 1, 1)).date()

    # Filter attendance records for the specified batch and month
    attendances = Attendance.objects.filter(
        batch=batch,
        date__range=(start_date, end_date)
    ).select_related('student').order_by('date', 'student__name')

    # Generate a dictionary to organize attendance by date
    attendance_by_date = {}
    for attendance in attendances:
        if attendance.date not in attendance_by_date:
            attendance_by_date[attendance.date] = []
        attendance_by_date[attendance.date].append(attendance)

    context = {
        'batch': batch,
        'attendance_by_date': attendance_by_date,
        'current_month': current_month,
        'current_year': current_year,
    }

    return render(request, 'attendance_view.html', context)



def export_attendance_to_excel(request, batch_id):
    # Fetch attendance records for the given batch
    attendances = Attendance.objects.filter(batch_id=batch_id)

    # Prepare data for the Excel sheet
    data = {
        'Serial Number': list(range(1, len(attendances) + 1)),  # Generate serial numbers
        'Date': [att.date.strftime('%Y-%m-%d') for att in attendances],  # Format date as YYYY-MM-DD
        'Batch Name': [att.batch.name for att in attendances],
        'Student Name': [att.student.name for att in attendances],
        'Present': ['Yes' if att.is_present else 'No' for att in attendances]  # Convert boolean to Yes/No
    }

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.xlsx"'

    # Write the DataFrame to the response
    df.to_excel(response, index=False, engine='openpyxl')

    return response

def send_absence_notification(student):
    subject = "Attendance Notification: Absent"
    message = f"Dear {student.parent_name or 'Parent'},\n\nYour child {student.name} was marked absent on {timezone.now().date()}.\n\nBest regards,\nYour School"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student.parent_email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

class StudentLoginView(View):
    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, 'student_login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Assuming your Student model has a one-to-one relationship with User
                student = user.student  # Adjust this line according to your models
                return redirect(reverse('student_page', kwargs={'student_id': student.id}))
            else:
                return redirect('student_login')  # Redirect to login page if authentication fails
        else:
            return render(request, 'student_login.html', {'form': form})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Save the message in the database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            # Optionally, you could redirect to a success page
            return redirect('index')  # Adjust accordingly

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def teampage(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'teacherdb'):
            # Redirect teachers to their page
            return redirect('teacher_page')
        elif hasattr(request.user, 'student'):
            # Redirect students to their page
            return redirect('student_page', student_id=request.user.student.id)

    teachers = TeacherDb.objects.all()
    return render(request, 'teampage.html', {'teachers': teachers})

@login_required
def Exampage(request):
    # Get the currently logged-in teacher
    teacher = get_object_or_404(TeacherDb, user=request.user)

    # Filter batches assigned to this teacher and include exams for each batch
    batches = Batch.objects.filter(teacher=teacher).prefetch_related('exam_batch')

    # Render the page with the filtered batches
    return render(request, 'Exampage.html', {'batches': batches})



@login_required
def add_exam(request, batch_id):
    teacher = get_object_or_404(TeacherDb, user=request.user)
    batch = get_object_or_404(Batch, id=batch_id)

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.batch = batch
            exam.department = teacher.department
            exam.save()
            return redirect('exam_page')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExamForm()

    return render(request, 'AddExampage.html', {
        'form': form,
        'batch': batch,
        'department': teacher.department,
    })

@login_required
def view_exams(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    exams = ExamDb.objects.filter(batch=batch)
    return render(request, 'ViewExams.html', {'batch': batch, 'exams': exams})


@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(ExamDb, id=exam_id)

    # Check if the number of existing questions has reached the limit
    existing_question_count = Question.objects.filter(exam=exam).count()
    existing_question_count = Question.objects.filter(exam=exam).count()
    total_question_number = exam.question_number

    # Prepare a flag to indicate if the limit is reached
    max_questions_reached = existing_question_count >= total_question_number

    if request.method == 'POST':
        if max_questions_reached:
            return redirect('view_questions', exam_id=exam_id)  # Redirect to the view questions page

        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            return redirect('view_questions', exam_id=exam_id)
    else:
        form = QuestionForm()

    return render(request, 'AddQuestion.html', {
        'form': form,
        'exam': exam,
        'questions_remaining': total_question_number - existing_question_count,
        'max_questions_reached': max_questions_reached
    })


@login_required
def view_questions(request, exam_id):
    exam = get_object_or_404(ExamDb, id=exam_id)
    questions = Question.objects.filter(exam=exam)


    total_question_number = exam.question_number
    current_question_count = questions.count()
    remaining_questions = total_question_number - current_question_count

    # Render the page with the additional context
    return render(request, 'view_questions.html', {
        'exam': exam,
        'questions': questions,
        'remaining_questions': remaining_questions,
    })


@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Check if the associated exam is active
    if question.exam.is_active:
        messages.error(request, 'Cannot edit question. Exam is already activated.')
        return redirect('view_questions', exam_id=question.exam.id)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('view_questions', exam_id=question.exam.id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'edit_question.html', {'form': form, 'question': question})


@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    # Check if the associated exam is active
    if question.exam.is_active:
        messages.error(request, 'Cannot delete question. Exam is already activated.')
        return redirect('view_questions', exam_id=question.exam.id)

    if request.method == 'POST':
        exam_id = question.exam.id
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        return redirect('view_questions', exam_id=exam_id)

    return render(request, 'confirm_delete.html', {'question': question})

def send_failure_email(student, exam, marks, total_marks):
    subject = 'Exam  Notification'
    message = (
        f'Dear {student.name},\n\n'
        f'We regret to inform you that you have not passed the exam "{exam.name}".\n'
        f'Your score: {marks}/{total_marks} ({(marks / total_marks) * 100:.2f}%)\n'
        f'Please reach out to your instructor for further guidance.\n\n'
        f'Best regards,\nYour School'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        logger.info(f"Failure email sent to {student.email}")
    except Exception as e:
        logger.error(f"Error sending email to {student.email}: {str(e)}")

def send_success_email(student, exam, marks, total_marks):
    subject = 'Exam  Notification'
    message = (
        f'Dear {student.name},\n\n'
        f'Congratulations! You have successfully passed the exam "{exam.name}".\n'
        f'Your score: {marks}/{total_marks} ({(marks / total_marks) * 100:.2f}%)\n'
        f'Well done on your achievement!\n\n'
        f'Best regards,\nYour School'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        logger.info(f"Success email sent to {student.email}")
    except Exception as e:
        logger.error(f"Error sending email to {student.email}: {str(e)}")




logger = logging.getLogger(__name__)


@login_required
def exam_results_page(request, batch_id, exam_id):
    # Get the batch and exam
    batch = get_object_or_404(Batch, id=batch_id)
    exam = get_object_or_404(ExamDb, id=exam_id, batch=batch)

    # Fetch results for the given exam
    results = Result.objects.filter(exam=exam).select_related('student')

    # Calculate the passing mark
    passing_percentage = 50  # Assuming 50% as the passing percentage
    total_marks = exam.max_marks
    passing_marks = total_marks * (passing_percentage / 100)

    # Prepare result data for rendering
    result_data = []
    for result in results:
        is_passed = result.marks >= passing_marks
        result_data.append({
            'student': result.student,
            'scored_marks': result.marks,
            'is_passed': is_passed,
            'total_mark':exam.max_marks,
        })

    return render(request, 'exam_results_page.html', {
        'exam': exam,
        'results': result_data,
        'batch': batch
    })
logger = logging.getLogger(__name__)


@login_required
def student_exam_page(request, exam_id):
    student = get_object_or_404(Student, user=request.user)
    exam = get_object_or_404(ExamDb, id=exam_id)

    logger.debug(f'Student ID: {student.id}, Exam ID: {exam.id}')

    # Check if the student has already taken the exam
    if Result.objects.filter(student=student, exam=exam).exists():
        messages.info(request, 'You have already taken this exam.')
        return redirect('exam_submission_success', exam_id=exam_id)

    questions = exam.question_set.all()

    if request.method == 'POST':
        # Process submitted answers
        correct_answers = {question.id: question.answer for question in questions}
        submitted_answers = {key: value for key, value in request.POST.items() if key.isdigit()}

        logger.debug(f'Submitted Answers: {submitted_answers}')
        logger.debug(f'Correct Answers: {correct_answers}')

        total_marks = sum(
            questions.get(id=int(question_id)).marks for question_id, submitted_answer in submitted_answers.items()
            if submitted_answer == correct_answers.get(int(question_id))
        )

        logger.debug(f'Total Marks Calculated: {total_marks}')

        # Save the result
        Result.objects.create(student=student, exam=exam, marks=total_marks)

        # Calculate passing marks
        passing_percentage = 50
        max_marks_exam = exam.max_marks
        passing_marks = (max_marks_exam * passing_percentage) / 100

        passed = total_marks >= passing_marks

        # Send email notifications
        if passed:
            send_success_email(student, exam, total_marks, max_marks_exam)
        else:
            send_failure_email(student, exam, total_marks, max_marks_exam)

        return render(request, 'exam_submission_success.html', {
            'total_marks': total_marks,
            'max_marks': max_marks_exam,
            'passing_marks': passing_marks,
            'passed': passed,
            'student': student,
            'exam': exam,
        })

    logger.debug(f'Rendering student_exam_page with student_id: {student.id}, exam_id: {exam.id}')

    # Calculate total duration and end time
    total_duration = exam.duration_hours * 60 + exam.duration_minutes
    end_time = timezone.now() + timedelta(minutes=total_duration)

    return render(request, 'student_exam_page.html', {
        'exam': exam,
        'questions': questions,
        'student_id': student.id,
        'end_time': end_time.timestamp(),  # Pass end time as a timestamp for JS
    })
@login_required
def exam_submission_success(request, exam_id):
    exam = get_object_or_404(ExamDb, id=exam_id)
    student = get_object_or_404(Student, user=request.user)

    # Retrieve the result for the student
    result = get_object_or_404(Result, student=student, exam=exam)
    total_marks = result.marks

    # Calculate passing marks
    passing_percentage = 50
    passing_marks = (exam.max_marks * passing_percentage) / 100

    # Determine pass/fail status
    passed = total_marks >= passing_marks

    context = {
        'exam': exam,
        'total_marks': total_marks,
        'max_marks': exam.max_marks,
        'passing_marks': passing_marks,
        'passed': passed,
        'student': student,
    }

    return render(request, 'exam_submission_success.html', context)



@login_required
def delete_exam(request):
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        batch_id = request.POST.get('batch_id')
        if exam_id:
            exam = get_object_or_404(ExamDb, id=exam_id)
            exam.delete()
            messages.success(request, 'Exam deleted successfully.')
            return redirect('view_exams', batch_id=batch_id)  # Redirect to the exams page
    return redirect('exam_page')  # Redirect to a relevant page if the request is invalid
@login_required
def activate_exam(request, exam_id):
    exam = get_object_or_404(ExamDb, id=exam_id)

    # Check if the user has permission to activate the exam
    teacher = get_object_or_404(TeacherDb, user=request.user)
    if exam.batch.teacher != teacher:
        return redirect('view_exams', batch_id=exam.batch.id)

    # Count existing questions
    existing_question_count = Question.objects.filter(exam=exam).count()
    total_question_number = exam.question_number  # Assuming this is defined in your model

    if existing_question_count < total_question_number:  # Check if there are remaining questions
        messages.error(request, 'Cannot activate exam. Please add all questions before activation.')
        return redirect('view_questions', exam_id=exam_id)

    if request.method == 'POST':
        exam.is_active = True
        exam.save()
        messages.success(request, 'Exam activated successfully.')

        # Notify students about the new exam
        notify_exam(exam.batch, exam)

    return redirect('view_questions', exam_id=exam_id)



def notify_exam(batch, exam):
    logger.info("Notifying students about the new exam...")

    try:
        # Get all students related to the batch
        students = batch.batch_students.all()
        logger.debug(f"Batch students: {students}")

        # Extract email addresses
        student_emails = list(students.values_list('student__user__email', flat=True))
        student_emails = list(filter(None, student_emails))  # Filter out any None or empty emails
        logger.debug(f"Student emails: {student_emails}")

        if not student_emails:
            logger.info("No student emails found.")
            return

        subject = 'New Exam Added'
        message = (
            f'A new exam has been added to your batch "{batch.name}".\n\n'
            f'Exam Name: {exam.name}\n'
            f'Exam Date: {exam.date}\n'
            f'Please check your dashboard and complete the exam before the end of the day.\n\n'
            f'For more details, please contact your faculty.'
        )
        from_email = settings.DEFAULT_FROM_EMAIL

        for email in student_emails:
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {email}")
            except Exception as e:
                logger.error(f"Error sending email to {email}: {str(e)}")

    except Exception as e:
        logger.error(f"Error retrieving students or sending emails: {str(e)}")



@login_required
def essay_exampage(request):
    teacher = get_object_or_404(TeacherDb, user=request.user)
    batches = Batch.objects.filter(teacher=teacher).prefetch_related('essay_exams')
    return render(request, 'EssayExampage.html', {'batches': batches})

@login_required
def add_essay_exam(request, batch_id):
    teacher = get_object_or_404(TeacherDb, user=request.user)
    batch = get_object_or_404(Batch, id=batch_id)

    if request.method == 'POST':
        form = EssayExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.batch = batch
            exam.department = teacher.department
            exam.save()
            messages.success(request, 'Essay exam added successfully.')
            return redirect('essay_exampage')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(form.errors)  # Debugging line to see form errors
    else:
        form = EssayExamForm()

    return render(request, 'AddEssayExampage.html', {
        'form': form,
        'batch': batch,
        'department': teacher.department,
    })



@login_required
def view_essay_exams(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    exams = Essay_Exam_Db.objects.filter(batch=batch)
    return render(request, 'ViewEssayExams.html', {
        'batch': batch,
        'exams': exams,
    })
@login_required
def edit_essay_exam(request, exam_id):
    exam = get_object_or_404(Essay_Exam_Db, id=exam_id)
    batch = exam.batch  # Get the associated batch
    current_date = timezone.now().date()  # Get today's date
    formatted_exam_date = exam.date.strftime('%Y-%m-%d')  # Format the date

    if request.method == 'POST':
        form = EssayExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Essay exam updated successfully.')
            return redirect('view_essay_exams', batch_id=batch.id)
    else:
        form = EssayExamForm(instance=exam)

    return render(request, 'EditEssayExamPage.html', {
        'form': form,
        'exam': exam,
        'current_date': current_date,
        'formatted_exam_date': formatted_exam_date,  # Pass the formatted date
        'batch': batch,  # Pass the batch to the template
    })

@login_required
def delete_essay_exam(request, exam_id):
    exam = get_object_or_404(Essay_Exam_Db, id=exam_id)
    batch = exam.batch  # Get the associated batch

    if request.method == 'POST':
        batch_id = exam.batch.id
        exam.delete()
        messages.success(request, 'Essay exam deleted successfully.')
        return redirect('view_essay_exams', batch_id=batch_id)

    return render(request, 'ConfirmDeleteEssayExam.html', {'exam': exam, 'batch': batch})  # Pass batch to template

@login_required
def essay_exam_results_page(request, batch_id, exam_id):
    batch = get_object_or_404(Batch, id=batch_id)
    exam = get_object_or_404(Essay_Exam_Db, id=exam_id)

    # Fetch the results for the specific exam
    results = exam.results.all()  # This will use the related_name defined in the Essay_Result model

    return render(request, 'EssayExamResultsPage.html', {
        'batch': batch,
        'exam': exam,
        'results': results,
    })


@login_required
def view_essay_exam_detail(request, batch_id, exam_id):
    batch = get_object_or_404(Batch, id=batch_id)  # Fetch the batch if needed
    exam = get_object_or_404(Essay_Exam_Db, id=exam_id)

    return render(request, 'ViewEssayExamDetail.html', {
        'exam': exam,
        'batch': batch,  # Pass the batch to the template if needed
    })
@login_required
def student_essay_exam_list(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Fetch essay exams related to the student's department
    essay_exams = Essay_Exam_Db.objects.filter(
        department=student.department,
        is_active=True
    ).exclude(
        id__in=Essay_StudentAnswer.objects.filter(student=student).values('exam_id')
    )

    return render(request, 'student_essay_exam_list.html', {
        'essay_exams': essay_exams,
        'student': student,
    })
@login_required
def student_essay_exam_page(request, batch_id):
    student = get_object_or_404(Student, user=request.user)

    # Fetch essay exams based on the provided batch ID
    essay_exams = Essay_Exam_Db.objects.filter(
        batch__id=batch_id,
        department=student.department,
        is_active=True
    )

    # Check if the student has already submitted an exam
    submitted_exams = Essay_StudentAnswer.objects.filter(student=student, exam__in=essay_exams)

    if submitted_exams.exists():
        # Instead of redirecting to index, render a page with a message
        return render(request, 'student_essay_exam_page.html', {
            'essay_exams': essay_exams,
            'student': student,
            'message': 'You have already submitted your answers for this exam.',
        })

    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        essay_answer = request.POST.get('essay_answer')

        # Ensure that essay_answer is provided
        if not essay_answer:
            return render(request, 'student_essay_exam_page.html', {
                'essay_exams': essay_exams,
                'student': student,
                'error': 'Please provide an answer for the essay.'
            })

        # Save the student's answer
        Essay_StudentAnswer.objects.create(
            student=student,
            exam_id=exam_id,
            essay_answer=essay_answer
        )

        return redirect('student_page', student.id)  # Change this to your home page URL

    return render(request, 'student_essay_exam_page.html', {
        'essay_exams': essay_exams,
        'student': student,
    })

@login_required
def student_attend_essay_exam(request, exam_id):
    student = get_object_or_404(Student, user=request.user)
    exam = get_object_or_404(Essay_Exam_Db, id=exam_id)

    # Check if the student has already attended this exam
    if Essay_StudentAnswer.objects.filter(student=student, exam=exam).exists():
        messages.error(request, "You have already attended this exam.")
        return redirect('student_page', student.id)  # Redirect to the student's page

    if request.method == 'POST':
        essay_answer = request.POST.get('essay_answer')

        # Ensure that essay_answer is provided
        if not essay_answer:
            messages.error(request, "Please provide an answer for the essay.")
            return redirect('student_attend_essay_exam', exam_id=exam.id)  # Redirect back to the exam page

        # Save the student's answer
        Essay_StudentAnswer.objects.create(
            student=student,
            exam=exam,
            essay_answer=essay_answer
        )

        messages.success(request, 'Your answer has been submitted successfully.')
        return redirect('student_page', student.id)

    return render(request, 'student_attend_essay_exam.html', {
        'exam': exam,
    })



@login_required
def activate_essay_exam(request, exam_id):
    exam = get_object_or_404(Essay_Exam_Db, id=exam_id)

    # Check if the user has permission to activate the exam
    teacher = get_object_or_404(TeacherDb, user=request.user)
    if exam.batch.teacher != teacher:
        messages.error(request, "You don't have permission to activate this exam.")
        return redirect('view_essay_exams', batch_id=exam.batch.id)

    # Activate the exam
    exam.is_active = True
    exam.save()
    messages.success(request, 'Essay exam activated successfully.')

    # Notify students about the new exam
    notify_exam(exam.batch, exam)

    return redirect('view_essay_exams', batch_id=exam.batch.id)

@login_required
def view_all_student_answers(request, exam_id):
    exam = get_object_or_404(Essay_Exam_Db, id=exam_id)
    student_answers = Essay_StudentAnswer.objects.filter(exam=exam)

    if request.method == 'POST':
        for answer in student_answers:
            mark_field = f'mark_{answer.id}'
            verified_field = f'verified_{answer.id}'

            mark = request.POST.get(mark_field)
            verified = request.POST.get(verified_field) is not None

            if mark:
                Essay_Result.objects.update_or_create(
                    student=answer.student,
                    exam=exam,
                    defaults={
                        'marks_scored': mark,
                        'is_verified': verified
                    }
                )

        messages.success(request, 'Marks and verification status updated successfully.')
        return redirect('view_all_student_answers', exam_id=exam.id)

    return render(request, 'view_all_student_answers.html', {
        'exam': exam,
        'student_answers': student_answers,
    })
@login_required
def view_student_answer_detail(request, answer_id):
    answer = get_object_or_404(Essay_StudentAnswer, id=answer_id)

    if request.method == 'POST':
        mark = request.POST.get('mark')
        verified = request.POST.get('verified') is not None

        if mark:
            Essay_Result.objects.update_or_create(
                student=answer.student,
                exam=answer.exam,
                defaults={
                    'marks_scored': mark,
                    'is_verified': verified
                }
            )
            messages.success(request, 'Marks and verification status updated successfully.')
            return redirect('view_all_student_answers', exam_id=answer.exam.id)

    return render(request, 'view_student_answer_detail.html', {
        'answer': answer,
    })


@login_required
def view_essay_exam_results(request, exam_id):
    exam = Essay_Exam_Db.objects.get(id=exam_id)
    results = Essay_Result.objects.filter(exam=exam)
    max_marks = exam.max_marks

    results_data = []
    for result in results:
        result.pass_fail = 'Pass' if result.marks_scored >= (max_marks * 0.5) else 'Fail'
        results_data.append({
            'student_name': result.student.name,
            'marks_scored': result.marks_scored,
            'pass_fail': result.pass_fail,
        })

    # Pass the batch ID as well
    batch_id = exam.batch.id  # Assuming you have a batch relation in Essay_Exam_Db

    return render(request, 'view_essay_exam_results.html', {
        'results_data': results_data,
        'batch_id': batch_id,
        'exam': exam,  # Optional, if you need exam details
    })


def aboutus(request):
    return render(request,'aboutus.html')


def policies(request):
    return render(request,'Policies.html')
def accreditation(request):
    return render(request,'accreditation.html')



def apply_online(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your application has been submitted successfully.")
            return redirect('apply_online')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ApplicationForm()

    return render(request, 'applyonline.html', {'form': form})

def student_jobs(request):
    return render(request,'student_jobs.html')

def student_visa(request):
    return render(request,'studnetvisa.html')

def student_portal(request):
    return render(request,'studnetportal.html')
def student_fee(request):
    return render(request,'student_fee.html')

def student_travel(request):
    return render(request,'student_travel.html')
def student_accommodation(request):
    return render(request,'accommodation.html')


def apply_accommodation(request):
    if request.method == 'POST':
        form = AccommodationApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('apply_accommodation')
    else:
        form = AccommodationApplicationForm()

    return render(request, 'apply_accommodation.html', {'form': form})

def apply_accommodation(request):
    if request.method == 'POST':
        form = AccommodationApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thanks_for_booking')  # Redirect to the new thank you page
    else:
        form = AccommodationApplicationForm()

    return render(request, 'apply_accommodation.html', {'form': form})

def thanks_for_booking(request):
    return render(request, 'thanks_for_booking.html')

def career_advice(request):
    return render(request,'career_advice.html')

def careerpage(request):
    return render(request,'careerpage.html')

def tourism_hospitality(request):
    return render(request,'tourism_hospitality.html')

def barista_training(request):
    return render(request,'barista.html')

def housekeeping(request):
    return render(request,'housekeeping.html')
def human_resource(request):
    return render(request,'human_resource.html')
def culinary_arts(request):
    return render(request,'culinary_arts.html')

def health_social(request):
    return render(request,'health_social.html')

def food_sanitation(request):
    return render(request,'food_sanitation.html')
def food_beverage(request):
    return render(request,'food_beverage.html')


def blog_news(request):
    return render(request,'blog_news.html')
def download_brochure(request):
    if request.method == 'POST':

        enquiry = Enquiry(
            name=request.POST['name'],
            email=request.POST['email'],
            mobile=request.POST['mobile'],
            course=request.POST['course']
        )
        enquiry.save()



    return redirect('index')
def enquiry_view(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()  # Save the enquiry to the database
            return redirect('index')  # Redirect to a success page or another page
    else:
        form = EnquiryForm()
    return render(request, 'enquiry.html', {'form': form})

@login_required
def staff_dashboard(request):
    departments = Department.objects.all()
    courses = CourseModules.objects.all()
    teachers = TeacherDb.objects.all()
    students = Student.objects.all()
    batches = Batch.objects.all()
    assignments = AssignmentUpload.objects.all()
    attendance_records = Attendance.objects.all()
    daily_topics = DailyTopic.objects.all()
    daily_assignments = DailyAssignment.objects.all()
    exams = ExamDb.objects.all()
    questions = Question.objects.all()
    results = Result.objects.all()
    accommodation_applications = AccommodationApplication.objects.all()
    enquiries = Enquiry.objects.all()

    context = {
        'departments': departments,
        'courses': courses,
        'teachers': teachers,
        'students': students,
        'batches': batches,
        'assignments': assignments,
        'attendance_records': attendance_records,
        'daily_topics': daily_topics,
        'daily_assignments': daily_assignments,
        'exams': exams,
        'questions': questions,
        'results': results,
        'accommodation_applications': accommodation_applications,
        'enquiries': enquiries,
    }

    return render(request, 'staff_dashboard.html', context)

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('staff_dashboard')  # Redirect to staff dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'staff_login.html')

# ///course
@login_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            course = form.save(commit=False)  # Do not save to database yet
            course.instructor = request.user  # Set the instructor
            course.save()  # Now save to database
            return redirect('course_list')  # Redirect to the list of courses
    else:
        form = CourseForm()

    return render(request, 'add_course.html', {'form': form})
@login_required
def course_list(request):
    courses = CourseModules.objects.all()
    return render(request, 'course_list.html', {'courses': courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(CourseModules, id=course_id)
    assigned_students = CourseStudent.objects.filter(course=course).select_related('student')

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'course_detail.html', {
        'course': course,
        'form': form,
        'assigned_students': assigned_students,  # Pass the assigned students
    })

@login_required
def assign_students_to_course(request, course_id):
    course = get_object_or_404(CourseModules, id=course_id)
    teacher = get_object_or_404(TeacherDb, user=request.user)
    students = Student.objects.filter(department=teacher.department)
    assigned_students = CourseStudent.objects.filter(course=course).values_list('student_id', flat=True)

    if request.method == 'POST':
        selected_students = request.POST.getlist('students')
        new_assignments = [
            CourseStudent(course=course, student_id=student_id)
            for student_id in selected_students if student_id not in assigned_students
        ]

        if new_assignments:
            CourseStudent.objects.bulk_create(new_assignments)

        return redirect('course_list')

    return render(request, 'assign_students_to_course.html', {
        'course': course,
        'students': students,
        'assigned_students': assigned_students,
    })



@login_required
def delete_course(request, course_id):
    course = get_object_or_404(CourseModules, id=course_id)

    if request.method == 'POST':
        course.delete()
        return redirect('course_list')  # Redirect to the course list after deletion

    return render(request, 'course_delete.html', {
        'course': course,
    })

@login_required
def student_courses(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    assigned_courses = CourseStudent.objects.filter(student=student).select_related('course')

    return render(request, 'student_courses.html', {
        'student': student,
        'assigned_courses': assigned_courses,
    })

@login_required
def student_course_detail(request, course_id):
    # Fetch the course based on the provided ID
    course = get_object_or_404(CourseModules, id=course_id)  # Ensure you use the correct model name
    student = request.user.student  # Assuming you have a related name to access the student

    return render(request, 'student_course_detail.html', {
        'course': course,
        'student': student
    })