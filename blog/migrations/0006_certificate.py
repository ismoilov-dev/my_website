from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_education_project_voluntaryactivity_workexperience_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('issuer', models.CharField(blank=True, help_text='e.g. Coursera, Udemy, Sfera Academy', max_length=200, null=True)),
                ('date', models.CharField(blank=True, help_text='e.g. 2024', max_length=100, null=True)),
                ('link', models.URLField(blank=True, help_text='Certificate URL if available', null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order', '-id'],
            },
        ),
    ]
