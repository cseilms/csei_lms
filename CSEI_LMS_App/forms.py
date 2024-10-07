import os
from django import forms
from .models import Student, TeacherDb, Batch, CourseModules, BatchFile, DailyTopic, DailyAssignment, AssignmentUpload, \
    Attendance, ExamDb, Question, Application, AccommodationApplication, Enquiry, Essay_Exam_Db

from django.utils import timezone


class CourseForm(forms.ModelForm):
    class Meta:
        model = CourseModules
        fields = [
            'course',
            'course_code',
            'time',
            'term_start_date',
            'term_end_date',
            'participation_limit',
            'upload_files',
            'description'
        ]
class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'phone', 'email',
            'parent_name', 'parent_phone', 'parent_email', 'address',
            'nationality', 'previous_education', 'image'
        ]
class StudentLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class TeacherRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = TeacherDb
        fields = ['name', 'email', 'password', 'phone_number', 'address', 'profile_picture', 'department', 'designation']

class TeacherLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name', 'schedule_date', 'schedule_time']

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        batch = super().save(commit=False)
        if self.teacher:
            batch.teacher = self.teacher
        if commit:
            batch.save()
        return batch

class AssignStudentsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if department:
            self.fields['students'].queryset = Student.objects.filter(department=department)

class BatchFileForm(forms.ModelForm):
    class Meta:
        model = BatchFile
        fields = ['title', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.mp3', '.mp4']
            ext = os.path.splitext(file.name)[1]
            if not ext.lower() in valid_extensions:
                raise forms.ValidationError('Unsupported file extension.')
        return file

class DailyTopicForm(forms.ModelForm):
    class Meta:
        model = DailyTopic
        fields = ['date', 'topics_covered']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'topics_covered': forms.Textarea(attrs={'rows': 5, 'cols': 40}),  # Adjust rows and cols as needed
        }
        labels = {
            'date': 'Date',
            'topics_covered': 'Topics Covered',
        }

class DailyAssignmentForm(forms.ModelForm):
    class Meta:
        model = DailyAssignment
        fields = ['date', 'assignments']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Use the HTML5 date input type for calendar picker
            'assignments': forms.Textarea(attrs={'rows': 5, 'cols': 40}),  # Customize textarea size
        }
        labels = {
            'date': 'Date',  # Label for the date field
            'assignments': 'Assignments',  # Label for the assignments field
        }
class AssignmentUploadForm(forms.ModelForm):
    class Meta:
        model = AssignmentUpload
        fields = ['title', 'file']


class AttendanceForm(forms.ModelForm):
    date = forms.DateField(required=True, label='Date', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Attendance
        fields = ['date']

    def __init__(self, *args, **kwargs):
        batch = kwargs.pop('batch', None)
        super().__init__(*args, **kwargs)
        if batch:
            self.fields['batch'] = forms.ModelChoiceField(
                queryset=Batch.objects.filter(id=batch.id),
                initial=batch,
                widget=forms.HiddenInput()
            )
            self.fields['students'] = forms.ModelMultipleChoiceField(
                queryset=Student.objects.filter(batch_students__batch=batch),
                widget=forms.CheckboxSelectMultiple,
                required=False
            )



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'placeholder': 'Message'}))


#Exam part
class ExamForm(forms.ModelForm):
    class Meta:
        model = ExamDb
        fields = ['name', 'date', 'duration_hours', 'duration_minutes', 'question_number', 'max_marks']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date(),  # Set minimum date to today
            }),
            'duration_hours': forms.NumberInput(attrs={'type': 'number', 'min': 0}),
            'duration_minutes': forms.NumberInput(attrs={'type': 'number', 'min': 0}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'option1', 'option2', 'option3', 'option4', 'answer']  # Exclude 'marks'
        widgets = {
            'question': forms.Textarea(attrs={'placeholder': 'Example: What is the relation calculus?'}),
            'option1': forms.TextInput(attrs={'placeholder': 'Example: It is a kind of procedural language'}),
            'option2': forms.TextInput(attrs={'placeholder': 'Example: It is a non-procedural language'}),
            'option3': forms.TextInput(attrs={'placeholder': 'Example: It is a high-level language'}),
            'option4': forms.TextInput(attrs={'placeholder': 'Example: It is Data Definition language'}),
            'answer': forms.Select(choices=Question._meta.get_field('answer').choices),  # Use the choices from the model
        }

    def save(self, commit=True):
        # Save the form instance with the default 'marks' value
        instance = super().save(commit=False)
        instance.marks = 1  # Set the default value for 'marks'
        if commit:
            instance.save()
        return instance



class StudentExamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        exam = kwargs.pop('exam')
        super().__init__(*args, **kwargs)
        questions = Question.objects.filter(exam=exam)
        for question in questions:
            choices = [
                (question.option1, question.option1),
                (question.option2, question.option2),
                (question.option3, question.option3),
                (question.option4, question.option4)
            ]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.question,
                choices=choices,
                widget=forms.RadioSelect
            )




class EssayExamForm(forms.ModelForm):
    class Meta:
        model = Essay_Exam_Db
        fields = ['name', 'description', 'date', 'duration_hours', 'duration_minutes', 'max_marks', 'max_words', 'instructions']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.now().date(),  # Set minimum date to today
            }),
            'duration_hours': forms.NumberInput(attrs={'type': 'number', 'min': 0}),
            'duration_minutes': forms.NumberInput(attrs={'type': 'number', 'min': 0}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter exam description...'}),
            'max_words': forms.NumberInput(attrs={'type': 'number', 'min': 0, 'placeholder': 'Max words'}),
            'instructions': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter basic instructions...'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'passport_number',
            'passport_expiry', 'nationality', 'birth_date', 'address',
            'mother_name', 'father_name', 'file', 'highest_qualification',
            'total_work_experience', 'interested_to_work',
            'contact_number_mother', 'contact_number_father',
            'guardian_name', 'guardian_phone', 'guardian_address_dubai',
            'gender', 'interested_program'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 4}),
            'interested_to_work': forms.Textarea(attrs={'rows': 4}),
            'guardian_address_dubai': forms.Textarea(attrs={'rows': 4}),
            'interested_to_work': forms.CheckboxInput()
        }

class AccommodationApplicationForm(forms.ModelForm):
    class Meta:
        model = AccommodationApplication
        fields = [
            'first_name',
            'gender',
            'email',
            'phone_number',
            'parent_contact_number',
            'uae_entry_date',
            'start_date_of_accommodation',
            'bed_space_option',
            'interested_program',
            'agree_terms'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'gender': forms.Select(),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'parent_contact_number': forms.TextInput(attrs={'placeholder': 'Enter parent contact number'}),
            'course_enrolled': forms.TextInput(attrs={'placeholder': 'Enter the course you are enrolled in'}),
            'uae_entry_date': forms.DateInput(attrs={'placeholder': 'MM/DD/YYYY', 'type': 'date'}),
            'start_date_of_accommodation': forms.DateInput(attrs={'placeholder': 'MM/DD/YYYY', 'type': 'date'}),
            'bed_space_option': forms.Select(choices=AccommodationApplication.BED_SPACE_OPTIONS),
            'interested_program': forms.Select(choices=[
                ('', 'Select a program'),
                ('tourism_hospitality', 'Tourism & Hospitality Management'),
                ('front_desk', 'Front Desk Operations'),
                ('barista_training', 'Barista Training Course'),
                ('human_resource_management', 'Human Resource Management in Hospitality and Tourism'),
                ('training_diploma_housekeeping', 'Training Diploma in Housekeeping'),
                ('food_safety', 'Food Safety Sanitation'),
                ('food_beverage_service', 'Food and Beverage Service Training'),
            ]),
            'agree_terms': forms.CheckboxInput(),
        }





class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'mobile', 'course']