"""Replace the initial skill list with the current technical stack.

The first skills migration seeded a starter list. This migration deliberately
updates those starter groups so existing installations show the same portfolio
content as a new one. Skill durations are removed: the page communicates
capability through its existing level treatment rather than elapsed time.
"""

from django.db import migrations


# (group name, tagline, [(skill name, level, highlight), ...])
TECHNICAL_SKILLS = [
    ('Languages', 'The foundations I build on', [
        ('Python', 5, True),
        ('JavaScript', 3, False),
        ('SQL', 4, False),
        ('HTML & CSS', 3, False),
        ('Bash', 3, False),
    ]),
    ('Backend', 'APIs, services and background work', [
        ('Django', 5, True),
        ('Django REST Framework (DRF)', 5, True),
        ('FastAPI', 4, False),
        ('Aiogram', 4, False),
        ('REST APIs', 5, False),
        ('Asynchronous processing', 4, False),
    ]),
    ('Frontend', 'Interfaces that connect people to products', [
        ('JavaScript', 3, False),
        ('React', 3, False),
    ]),
    ('Data', 'Reliable storage and fast retrieval', [
        ('PostgreSQL', 4, True),
        ('SQLite', 4, False),
        ('Redis', 4, False),
    ]),
    ('Cloud & DevOps', 'Shipping and operating production services', [
        ('Celery', 4, False),
        ('Docker', 4, True),
        ('Linux VPS', 4, False),
        ('Nginx', 4, False),
        ('Gunicorn', 4, False),
        ('Git', 5, False),
        ('GitHub CI/CD', 3, False),
    ]),
    ('Quality & AI', 'Testing, AI integrations and automation', [
        ('Pytest', 4, False),
        ('Anthropic Claude API', 4, False),
        ('Prompt engineering', 4, True),
        ('Automated content-generation pipelines', 4, False),
    ]),
]


def refresh_skills(apps, schema_editor):
    SkillGroup = apps.get_model('blog', 'SkillGroup')
    Skill = apps.get_model('blog', 'Skill')

    # These are the original seeded groups, renamed where the new taxonomy
    # calls for it. Removing their children prevents obsolete starter skills
    # from lingering alongside the current portfolio stack.
    old_names = ('Languages', 'Backend', 'Data', 'Delivery', 'AI & Automation')
    Skill.objects.filter(group__name__in=old_names).delete()

    renamed_groups = {
        'Delivery': 'Cloud & DevOps',
        'AI & Automation': 'Quality & AI',
    }
    for old_name, new_name in renamed_groups.items():
        SkillGroup.objects.filter(name=old_name).update(name=new_name)

    for group_order, (name, tagline, skills) in enumerate(TECHNICAL_SKILLS):
        group, _ = SkillGroup.objects.get_or_create(name=name)
        group.tagline = tagline
        group.order = group_order
        group.save(update_fields=('tagline', 'order'))
        Skill.objects.bulk_create([
            Skill(group=group, name=skill, level=level, is_core=is_core, order=order)
            for order, (skill, level, is_core) in enumerate(skills)
        ])


class Migration(migrations.Migration):

    dependencies = [('blog', '0018_skill_wording')]

    operations = [
        migrations.RunPython(refresh_skills, migrations.RunPython.noop),
        migrations.RemoveField(model_name='skill', name='years'),
    ]
