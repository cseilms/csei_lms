import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


class TeacherDb(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    approved = models.BooleanField(default=False)
    teacher_id = models.CharField(max_length=50, null=True, blank=True)  # New field for Teacher ID

    def __str__(self):
        return self.name
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)  # Parent's phone number
    parent_email = models.EmailField(blank=True, null=True)  # Parent's email address
    parent_name = models.CharField(max_length=100, blank=True, null=True)  # Parent's name
    address = models.TextField(blank=True, null=True)  # Parent's address
    nationality = models.CharField(max_length=50, blank=True, null=True)
    previous_education = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    has_paid = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    generated_password = models.CharField(max_length=128, blank=True, null=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)  # Student ID

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.name
class CourseModules(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True)  # ForeignKey to Course
    course_code = models.CharField(max_length=50)
    time = models.TimeField(null=True)
    term_start_date = models.DateField()
    term_end_date = models.DateField()
    participation_limit = models.BooleanField(default=False)
    upload_files = models.FileField(upload_to='course_uploads/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # New description field

    def __str__(self):
        return f" {self.course_code}"  # Update __str__ method


class CourseStudent(models.Model):
    course = models.ForeignKey(CourseModules, on_delete=models.CASCADE, related_name='course_students')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_students')
    date_joined = models.DateTimeField(auto_now_add=True)


class Batch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    schedule_date = models.DateField()
    schedule_time = models.TimeField()
    students = models.ManyToManyField(Student, related_name='batches', blank=True)
    teacher = models.ForeignKey(TeacherDb, on_delete=models.SET_NULL, null=True, blank=True, related_name='batches')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    has_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'Batch'
        verbose_name_plural = 'Batches'
        ordering = ['schedule_date', 'schedule_time']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/batches/{self.id}/"

class BatchStudent(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='batch_students')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='batch_students')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Batch Student'
        verbose_name_plural = 'Batch Students'
        unique_together = ('batch', 'student')

    def __str__(self):
        return f"{self.student.name} in {self.batch.name} (Joined on {self.date_joined})"

class BatchFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='batch_files/')
    batch = models.ForeignKey(Batch, related_name='files', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Batch File'
        verbose_name_plural = 'Batch Files'

    def __str__(self):
        return self.title

class DailyTopic(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='daily_topics')
    date = models.DateField(default=timezone.now)
    topics_covered = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Daily Topic'
        verbose_name_plural = 'Daily Topics'
        ordering = ['date']

    def __str__(self):
        return f"{self.batch.name} - {self.date}"

class DailyAssignment(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='daily_assignments')
    date = models.DateField(default=timezone.now)
    assignments = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Daily Assignment'
        verbose_name_plural = 'Daily Assignments'
        ordering = ['date']

    def __str__(self):
        return f"{self.batch.name} - {self.date}"





class AssignmentUpload(models.Model):
    title = models.CharField(max_length=255, default='', null=False)
    file = models.FileField(upload_to='uploads/assignments/', default='path/to/default/file', null=False)
    upload_date = models.DateField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='uploads', null=True, blank=True)
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='assignment_uploads', null=True)

    class Meta:
        verbose_name = 'Assignment Upload'
        verbose_name_plural = 'Assignment Uploads'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

class Attendance(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('batch', 'student', 'date')
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'

    def __str__(self):
        return f"{self.student.name} - {self.batch.name} - {self.date}"
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

class ExamDb(models.Model):
    name = models.CharField(max_length=20)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='exam_batch')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    duration_hours = models.PositiveIntegerField(default=0)  # Separate field for hours
    duration_minutes = models.PositiveIntegerField(default=0)  # Separate field for minutes
    question_number = models.PositiveIntegerField()
    max_marks = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)

    @property
    def total_duration(self):
        return f"{self.duration_hours} hours {self.duration_minutes} minutes"

    def __str__(self):
        return self.name
class Question(models.Model):
    exam = models.ForeignKey(ExamDb, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    cat = (
        ('Option1', 'Option1'),
        ('Option2', 'Option2'),
        ('Option3', 'Option3'),
        ('Option4', 'Option4')
    )
    answer = models.CharField(max_length=200, choices=cat)

    def __str__(self):
        return f"{self.question} (ID: {self.id})"

    def get_batch_name(self):
        return self.exam.batch.name

    def get_exam_name(self):
        return self.exam.name


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamDb, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamDb, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)

    def __str__(self):
        return f"Student: {self.student}, Question: {self.question}, Answer: {self.answer}"

# essay exam


class Essay_Exam_Db(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()  # This can serve as the essay prompt
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='essay_exams')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    duration_hours = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    max_marks = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)

    # New fields
    max_words = models.PositiveIntegerField(default=0)  # Maximum words allowed for the essay
    instructions = models.TextField(blank=True, null=True)  # Basic instructions for the exam


    @property
    def total_duration(self):
        return f"{self.duration_hours} hours {self.duration_minutes} minutes"

    def __str__(self):
        return self.name


class Essay_Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Essay_Exam_Db, on_delete=models.CASCADE, related_name='results')
    marks_scored = models.PositiveIntegerField()
    is_verified = models.BooleanField(default=False)  # New field for verification status
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.exam} ({self.marks_scored} marks)"


class Essay_StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Essay_Exam_Db, on_delete=models.CASCADE, related_name='student_answers')
    essay_answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"Student: {self.student}, Exam: {self.exam.name}, Answer: {self.essay_answer[:30]}..."  # Display first 30 chars


class Application(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passport_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    course = models.CharField(max_length=255, null=True)
    passport_number = models.CharField(max_length=50, null=True)
    passport_expiry = models.DateField(null=True)
    nationality = models.CharField(max_length=100, null=True)
    interested_program = models.TextField(blank=True)  # Change this to CharField if you want dropdown
    birth_date = models.DateField()
    address = models.TextField()
    mother_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='applications/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.course}"

class AccommodationApplication(models.Model):
    BED_SPACE_OPTIONS = [
        ('3_person', '3 Person sharing room bed space: 900AED / month rent'),
        ('4_person', '4 Person sharing room bed space: 750AED / month rent'),
        # Add more options if necessary
    ]

    first_name = models.CharField(max_length=100, verbose_name="First Name")
    course_enrolled = models.CharField(max_length=255, verbose_name="Course Enrolled")
    uae_entry_date = models.DateField(verbose_name="UAE Entry Date")
    start_date_of_accommodation = models.DateField(verbose_name="Start Date of Accommodation")
    bed_space_option = models.CharField(
        max_length=20,
        choices=BED_SPACE_OPTIONS,
        verbose_name="Select Bed Space Option"
    )

    def __str__(self):
        return f"{self.first_name} - {self.course_enrolled}"



class Enquiry(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    course = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name