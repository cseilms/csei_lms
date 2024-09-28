# Generated by Django 5.1 on 2024-09-27 11:23

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccommodationApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='First Name')),
                ('course_enrolled', models.CharField(max_length=255, verbose_name='Course Enrolled')),
                ('uae_entry_date', models.DateField(verbose_name='UAE Entry Date')),
                ('start_date_of_accommodation', models.DateField(verbose_name='Start Date of Accommodation')),
                ('bed_space_option', models.CharField(choices=[('3_person', '3 Person sharing room bed space: 900AED / month rent'), ('4_person', '4 Person sharing room bed space: 750AED / month rent')], max_length=20, verbose_name='Select Bed Space Option')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('passport_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('course', models.CharField(max_length=255, null=True)),
                ('passport_number', models.CharField(max_length=50, null=True)),
                ('passport_expiry', models.DateField(null=True)),
                ('nationality', models.CharField(max_length=100, null=True)),
                ('interested_program', models.TextField(blank=True)),
                ('birth_date', models.DateField()),
                ('address', models.TextField()),
                ('mother_name', models.CharField(max_length=255)),
                ('father_name', models.CharField(max_length=255)),
                ('file', models.FileField(blank=True, null=True, upload_to='applications/')),
            ],
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
            },
        ),
        migrations.CreateModel(
            name='Enquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('mobile', models.CharField(max_length=15)),
                ('course', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('schedule_date', models.DateField()),
                ('schedule_time', models.TimeField()),
                ('has_paid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='CSEI_LMS_App.department')),
            ],
            options={
                'verbose_name': 'Batch',
                'verbose_name_plural': 'Batches',
                'ordering': ['schedule_date', 'schedule_time'],
            },
        ),
        migrations.CreateModel(
            name='BatchFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='batch_files/')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='CSEI_LMS_App.batch')),
            ],
            options={
                'verbose_name': 'Batch File',
                'verbose_name_plural': 'Batch Files',
            },
        ),
        migrations.CreateModel(
            name='CourseModules',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=50)),
                ('time', models.TimeField(null=True)),
                ('term_start_date', models.DateField()),
                ('term_end_date', models.DateField()),
                ('participation_limit', models.BooleanField(default=False)),
                ('upload_files', models.FileField(blank=True, null=True, upload_to='course_uploads/')),
                ('description', models.TextField(blank=True, null=True)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.course')),
            ],
        ),
        migrations.CreateModel(
            name='DailyAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('assignments', models.TextField(blank=True, null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_assignments', to='CSEI_LMS_App.batch')),
            ],
            options={
                'verbose_name': 'Daily Assignment',
                'verbose_name_plural': 'Daily Assignments',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='DailyTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('topics_covered', models.TextField(blank=True, null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_topics', to='CSEI_LMS_App.batch')),
            ],
            options={
                'verbose_name': 'Daily Topic',
                'verbose_name_plural': 'Daily Topics',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Essay_Exam_Db',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('date', models.DateField()),
                ('duration_hours', models.PositiveIntegerField(default=0)),
                ('duration_minutes', models.PositiveIntegerField(default=0)),
                ('max_marks', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=False)),
                ('max_words', models.PositiveIntegerField(default=0)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='essay_exams', to='CSEI_LMS_App.batch')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.department')),
            ],
        ),
        migrations.CreateModel(
            name='ExamDb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('date', models.DateField()),
                ('duration_hours', models.PositiveIntegerField(default=0)),
                ('duration_minutes', models.PositiveIntegerField(default=0)),
                ('question_number', models.PositiveIntegerField()),
                ('max_marks', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=False)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_batch', to='CSEI_LMS_App.batch')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.department')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks', models.PositiveIntegerField()),
                ('question', models.CharField(max_length=600)),
                ('option1', models.CharField(max_length=200)),
                ('option2', models.CharField(max_length=200)),
                ('option3', models.CharField(max_length=200)),
                ('option4', models.CharField(max_length=200)),
                ('answer', models.CharField(choices=[('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4')], max_length=200)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.examdb')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('parent_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('nationality', models.CharField(blank=True, max_length=50, null=True)),
                ('previous_education', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='student_images/')),
                ('has_paid', models.BooleanField(default=False)),
                ('generated_password', models.CharField(blank=True, max_length=128, null=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='CSEI_LMS_App.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.examdb')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.student')),
            ],
        ),
        migrations.CreateModel(
            name='Essay_StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('essay_answer', models.TextField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_answers', to='CSEI_LMS_App.essay_exam_db')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.student')),
            ],
        ),
        migrations.CreateModel(
            name='Essay_Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks_scored', models.PositiveIntegerField()),
                ('is_verified', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='CSEI_LMS_App.essay_exam_db')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.student')),
            ],
        ),
        migrations.AddField(
            model_name='batch',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='batches', to='CSEI_LMS_App.student'),
        ),
        migrations.CreateModel(
            name='AssignmentUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('file', models.FileField(default='path/to/default/file', upload_to='uploads/assignments/')),
                ('upload_date', models.DateField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignment_uploads', to='CSEI_LMS_App.batch')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploads', to='CSEI_LMS_App.student')),
            ],
            options={
                'verbose_name': 'Assignment Upload',
                'verbose_name_plural': 'Assignment Uploads',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=200)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.examdb')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.question')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.student')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherDb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('designation', models.CharField(blank=True, max_length=50, null=True)),
                ('password', models.CharField(blank=True, max_length=128, null=True)),
                ('approved', models.BooleanField(default=False)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='CSEI_LMS_App.department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='batch',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='batches', to='CSEI_LMS_App.teacherdb'),
        ),
        migrations.CreateModel(
            name='CourseStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_students', to='CSEI_LMS_App.coursemodules')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_students', to='CSEI_LMS_App.student')),
            ],
            options={
                'unique_together': {('course', 'student')},
            },
        ),
        migrations.CreateModel(
            name='BatchStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_students', to='CSEI_LMS_App.batch')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_students', to='CSEI_LMS_App.student')),
            ],
            options={
                'verbose_name': 'Batch Student',
                'verbose_name_plural': 'Batch Students',
                'unique_together': {('batch', 'student')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('is_present', models.BooleanField(default=False)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='CSEI_LMS_App.batch')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='CSEI_LMS_App.student')),
            ],
            options={
                'verbose_name': 'Attendance',
                'verbose_name_plural': 'Attendances',
                'unique_together': {('batch', 'student', 'date')},
            },
        ),
    ]
