from django.urls import path
from CSEI_LMS_App import views
from .views import StudentLoginView

urlpatterns = [
    # Homepage and Info Pages
    path('', views.index, name='index'),
    path('download-brochure/', views.download_brochure, name='download_brochure'),
    path('contact/', views.contact, name='contact'),
    path('teampage/', views.teampage, name='teampage'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('policies/', views.policies, name='policies'),
    path('accreditation/', views.accreditation, name='accreditation'),
    path('apply/', views.apply_online, name='apply_online'),
    path('student_jobs/', views.student_jobs, name='student_jobs'),
    path('student_visa/', views.student_visa, name='student_visa'),
    path('student_portal/', views.student_portal, name='student_portal'),
    path('student_fee/', views.student_fee, name='student_fee'),
    path('student_travel/', views.student_travel, name='student_travel'),
    path('student_accommodation/', views.student_accommodation, name='student_accommodation'),
    path('careerpage/', views.careerpage, name='careerpage'),
    path('tourism_hospitality/', views.tourism_hospitality, name='tourism_hospitality'),
    path('barista/', views.barista_training, name='barista_training'),
    path('housekeeping/', views.housekeeping, name='housekeeping'),
    path('blog_news/', views.blog_news, name='blog_news'),

    path('human_resource/', views.human_resource, name='human_resource'),
    path('culinary_arts/', views.culinary_arts, name='culinary_arts'),
    path('health_social/', views.health_social, name='health_social'),
    path('food_sanitation/', views.food_sanitation, name='food_sanitation'),
    path('food_beverage/', views.food_beverage, name='food_beverage'),
    path('enquiry_view/', views.enquiry_view, name='enquiry_view'),

    # Registration
    path('student_register/', views.student_register, name='student_register'),
    path('teacher_register/', views.teacher_register, name='teacher_register'),
    path('apply_accommodation/', views.apply_accommodation, name='apply_accommodation'),
    path('thanks_for_booking/', views.thanks_for_booking, name='thanks_for_booking'),
    path('career_advice/', views.career_advice, name='career_advice'),

    # Login and Logout
    path('teacher_login/', views.teacher_login, name='teacher_login'),
    path('logout/', views.user_logout, name='logout'),
    path('staff-login/', views.staff_login, name='staff_login'),

    # Pages
    path('teacher_page/', views.teacher_page, name='teacher_page'),
    path('student_page/<int:student_id>/', views.student_page, name='student_page'),

    # Batch Management
    path('add_batch/', views.add_batch, name='add_batch'),
    path('assign_students_to_batch/<int:batch_id>/', views.assign_student_to_batch, name='assign_students_to_batch'),

    # Batch Details
    path('batch/<int:batch_id>/student-files/', views.student_view_files, name='student_view_files'),
    path('batch/<int:batch_id>/details/', views.student_batch_details, name='student_batch_details'),
    path('batch_details/<int:id>/', views.batch_details, name='batch_details'),

    # File Management
    path('add_file_to_batch/<int:batch_id>/', views.add_file_to_batch, name='add_file_to_batch'),
    path('teacher_view_files/<int:batch_id>/', views.teacher_view_files, name='teacher_view_files'),
    path('replace_batch_file/<int:batch_id>/<int:file_id>/', views.replace_batch_file, name='replace_batch_file'),
    path('delete_batch_file/<int:batch_id>/<int:file_id>/', views.delete_batch_file, name='delete_batch_file'),
    path('view-batch-details/', views.view_batch_details, name='view_batch_details'),

    # Assignments
    path('upload_assignment/<int:batch_id>/', views.upload_assignment, name='upload_assignment'),
    path('add_assignment/<int:batch_id>/', views.add_assignment, name='add_assignment'),
    path('batch/<int:batch_id>/assignments/', views.student_assignments, name='student_assignments'),

    # Topics and Assignments
    path('add_topic/<int:batch_id>/', views.add_topic, name='add_topic'),
    path('batch/<int:batch_id>/daily_assignment/', views.view_daily_assignment, name='view_daily_assignment'),
    path('batch/<int:batch_id>/daily_topic/', views.view_daily_topic, name='view_daily_topic'),

    # Student Login
    path('student_login/', StudentLoginView.as_view(), name='student_login'),

    # Attendance
    path('attendance_form/<int:batch_id>/', views.attendance_form_view, name='attendance_form_view'),
    path('attendance_view/<int:batch_id>/', views.attendance_view, name='attendance_view'),
    path('attendance_export/<int:batch_id>/', views.export_attendance_to_excel, name='export_attendance_to_excel'),

    # Exam Management
    path('add_exam/<int:batch_id>/', views.add_exam, name='add_exam'),
    path('exam_page/', views.Exampage, name='exam_page'),
    path('view_exams/<int:batch_id>/', views.view_exams, name='view_exams'),
    path('add_question/<int:exam_id>/', views.add_question, name='add_question'),
    path('activate_exam/<int:exam_id>/', views.activate_exam, name='activate_exam'),
    path('questions/<int:exam_id>/', views.view_questions, name='view_questions'),
    path('question/edit/<int:question_id>/', views.edit_question, name='edit_question'),
    path('question/delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('activate-essay-exam/<int:exam_id>/', views.activate_essay_exam, name='activate_essay_exam'),
    path('exam/<int:exam_id>/', views.student_exam_page, name='student_exam_page'),
    path('exam_results/<int:batch_id>/<int:exam_id>/', views.exam_results_page, name='exam_results_page'),
    path('batch/<int:batch_id>/exams/', views.student_view_exams, name='student_view_exams'),
    path('delete_exam/', views.delete_exam, name='delete_exam'),
    path('exam-submission-success/<int:exam_id>/', views.exam_submission_success, name='exam_submission_success'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),

    # Essay Exam Management
    path('essay_exampage/', views.essay_exampage, name='essay_exampage'),
    path('essay-exams/add/<int:batch_id>/', views.add_essay_exam, name='add_essay_exam'),
    path('essay-exams/view/<int:batch_id>/', views.view_essay_exams, name='view_essay_exams'),
    path('essay-exams/edit/<int:exam_id>/', views.edit_essay_exam, name='edit_exam'),
    path('delete_essay_exam/<int:exam_id>/', views.delete_essay_exam, name='delete_essay_exam'),
    path('essay-exam-results/<int:batch_id>/<int:exam_id>/', views.essay_exam_results_page, name='essay_exam_results_page'),
    path('view_essay_exam_detail/<int:batch_id>/<int:exam_id>/', views.view_essay_exam_detail, name='view_essay_exam_detail'),
    path('student/essay-exams/<int:batch_id>/', views.student_essay_exam_page, name='student_essay_exam_page'),
    path('student/essay-exams/attend/<int:exam_id>/', views.student_attend_essay_exam, name='student_attend_essay_exam'),
    path('exam/<int:exam_id>/student/answers/', views.view_all_student_answers, name='view_all_student_answers'),
    path('student/answer/<int:answer_id>/', views.view_student_answer_detail, name='view_student_answer_detail'),
    path('exam-results/<int:exam_id>/', views.view_essay_exam_results, name='view_essay_exam_results'),

    path('add_course/', views.add_course, name='add_course'),
    path('course_list', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('assign_students_to_course/<int:course_id>/', views.assign_students_to_course, name='assign_students_to_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
path('student/<int:student_id>/courses/', views.student_courses, name='student_courses'),
    path('student/<int:student_id>/essay-exams/', views.student_essay_exam_list, name='student_essay_exam_list'),
path('student_course_detail/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
]
