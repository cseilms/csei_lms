# Generated by Django 5.1 on 2024-09-27 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CSEI_LMS_App', '0003_student_parent_address_student_parent_email_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='parent_address',
            new_name='address',
        ),
    ]
