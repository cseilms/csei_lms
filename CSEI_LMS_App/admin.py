from django.contrib import admin
from .models import Department, AssignmentUpload, CourseModules, TeacherDb, Student, Batch, BatchStudent, BatchFile, \
    DailyTopic, DailyAssignment, Attendance, ContactMessage, ExamDb, Question, Result, Application, \
    AccommodationApplication, Enquiry, Essay_StudentAnswer, Essay_Exam_Db, Essay_Result, Course


# Registering Department model
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Registering Course model

# Registering TeacherDb model
@admin.register(TeacherDb)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'phone_number', 'department', 'designation', 'approved')
    search_fields = ('user__username', 'user__email', 'name')
    list_filter = ('department', 'designation', 'approved')

# Registering AssignmentUpload model

@admin.register(AssignmentUpload)
class AssignmentUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'upload_date', 'student', 'batch')
    search_fields = ('title',)
    list_filter = ('upload_date', 'student', 'batch')

# Registering Student model
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'department')
    search_fields = ('name', 'email')
    list_filter = ('department',)

# Registering Batch model
@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'schedule_date', 'schedule_time', 'teacher')
    list_filter = ('teacher', 'schedule_date', 'department')
    search_fields = ('name',)

# Registering BatchStudent model
@admin.register(BatchStudent)
class BatchStudentAdmin(admin.ModelAdmin):
    list_display = ('batch', 'student', 'date_joined')
    search_fields = ('batch__name', 'student__name')
    list_filter = ('batch', 'date_joined')

# Registering BatchFile model
@admin.register(BatchFile)
class BatchFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'batch')
    search_fields = ('title', 'batch__name')
    list_filter = ('batch',)

# Registering DailyTopic model
@admin.register(DailyTopic)
class DailyTopicAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'topics_covered')
    search_fields = ('batch__name', 'topics_covered')
    list_filter = ('batch', 'date')

# Registering DailyAssignment model
@admin.register(DailyAssignment)
class DailyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('batch', 'date', 'assignments')
    search_fields = ('batch__name', 'assignments')
    list_filter = ('batch', 'date')


# Registering Attendance model
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('batch', 'student', 'date', 'is_present')
    list_filter = ('batch', 'date', 'is_present')
    search_fields = ('batch__name', 'student__name')

admin.site.register(ContactMessage)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_exam_name', 'get_batch_name', 'marks', 'answer')

    def get_exam_name(self, obj):
        return obj.exam.name
    get_exam_name.admin_order_field = 'exam'  # Allow sorting by exam
    get_exam_name.short_description = 'Exam Name'

    def get_batch_name(self, obj):
        return obj.exam.batch.name
    get_batch_name.admin_order_field = 'exam__batch'  # Allow sorting by batch
    get_batch_name.short_description = 'Batch Name'

    # Optional: Add search functionality
    search_fields = ('question', 'exam__name', 'exam__batch__name')


class ExamDbAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch', 'department', 'date', 'duration_hours', 'duration_minutes', 'question_number', 'max_marks')

admin.site.register(ExamDb, ExamDbAdmin)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks', 'date')

class AccommodationApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'course_enrolled', 'uae_entry_date', 'start_date_of_accommodation', 'bed_space_option')
    search_fields = ('first_name', 'course_enrolled')
    list_filter = ('bed_space_option', 'uae_entry_date')
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'course', 'created_at')  # Fields to display in the list view
    search_fields = ('name', 'email', 'course')  # Fields that can be searched
    list_filter = ('course', 'created_at')  # Filters available in the sidebar
    ordering = ('-created_at',)  # Order by creation date descending
    date_hierarchy = 'created_at'  # Adds a date-based drilldown navigation
admin.site.register(AccommodationApplication, AccommodationApplicationAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Application)
admin.site.register(Essay_StudentAnswer)
admin.site.register(Essay_Result)
admin.site.register(Essay_Exam_Db)
admin.site.register(CourseModules)
admin.site.register(Course)