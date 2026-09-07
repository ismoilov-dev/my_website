"""Seed the /cv/ skill map so the section is never an empty circle.

Everything here is ordinary content: edit it, reorder it or delete it from the
admin. The migration only runs on a database that has no skill groups yet, so
later edits are never overwritten by a redeploy.
"""

from django.db import migrations

# (group, tagline, [(skill, level, years, is_core), ...])
SEED = [
    ('Languages', 'What I think in', [
        ('SQL', 4, '4y', False),
        ('JavaScript', 3, '3y', False),
        ('HTML & CSS', 3, '4y', False),
        ('Bash', 3, '', False),
    ]),
    ('Backend', 'Where most of my hours go', [
        ('Django', 5, '4y', True),
        ('Django REST Framework', 5, '4y', True),
        ('FastAPI', 4, '2y', False),
        ('Celery', 4, '2y', False),
        ('aiogram', 4, '3y', False),
        ('REST API design', 5, '', False),
    ]),
    ('Data', 'Storing it and getting it back fast', [
        ('PostgreSQL', 4, '4y', True),
        ('Redis', 4, '2y', False),
        ('SQLite', 4, '', False),
        ('ORM & migrations', 4, '', False),
    ]),
    ('Delivery', 'Getting it onto a server and keeping it there', [
        ('Docker', 4, '3y', True),
        ('Nginx', 4, '3y', False),
        ('Gunicorn', 4, '', False),
        ('GitHub Actions', 3, '2y', False),
        ('Linux', 4, '4y', False),
        ('Git', 5, '4y', False),
    ]),
    ('AI & Automation', 'The part I keep experimenting with', [
        ('OpenAI API', 4, '2y', False),
        ('LLM integrations', 4, '2y', True),
        ('Web scraping', 4, '3y', False),
        ('Telegram bots', 5, '3y', False),
    ]),
]


def seed(apps, schema_editor):
    SkillGroup = apps.get_model('blog', 'SkillGroup')
    Skill = apps.get_model('blog', 'Skill')

    if SkillGroup.objects.exists():
        return

    for group_order, (name, tagline, skills) in enumerate(SEED):
        group = SkillGroup.objects.create(name=name, tagline=tagline, order=group_order)
        Skill.objects.bulk_create([
            Skill(
                group=group, name=skill, level=level, years=years,
                is_core=is_core, order=order,
            )
            for order, (skill, level, years, is_core) in enumerate(skills)
        ])


def unseed(apps, schema_editor):
    """Remove only the seeded groups, leaving anything hand-added in place."""
    SkillGroup = apps.get_model('blog', 'SkillGroup')
    SkillGroup.objects.filter(name__in=[name for name, _, _ in SEED]).delete()


class Migration(migrations.Migration):

    dependencies = [('blog', '0016_skillgroup_skill')]

    operations = [migrations.RunPython(seed, unseed)]
