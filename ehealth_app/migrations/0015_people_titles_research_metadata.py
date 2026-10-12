from django.db import migrations, models
import django.db.models.deletion


def migrate_titles(apps, schema_editor):
    People = apps.get_model('ehealth_app', 'People')
    Title = apps.get_model('ehealth_app', 'PeopleTitle')
    alias = schema_editor.connection.alias
    for name in ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Assoc. Prof.', 'Prof.']:
        Title.objects.using(alias).get_or_create(name=name)
    for person in People.objects.using(alias).exclude(legacy_title=''):
        title, _ = Title.objects.using(alias).get_or_create(name=person.legacy_title)
        People.objects.using(alias).filter(pk=person.pk).update(title_id=title.pk)


def restore_titles(apps, schema_editor):
    People = apps.get_model('ehealth_app', 'People')
    alias = schema_editor.connection.alias
    for person in People.objects.using(alias).select_related('title'):
        People.objects.using(alias).filter(pk=person.pk).update(
            legacy_title=person.title.name if person.title else '',
        )


class Migration(migrations.Migration):
    dependencies = [('ehealth_app', '0014_peopleresearchlink')]
    operations = [
        migrations.CreateModel(
            name='PeopleTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.RenameField(model_name='people', old_name='title', new_name='legacy_title'),
        migrations.AddField(
            model_name='people', name='title',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='people', to='ehealth_app.peopletitle'),
        ),
        migrations.RunPython(migrate_titles, restore_titles),
        migrations.RemoveField(model_name='people', name='legacy_title'),
        migrations.AddField(model_name='peopleresearchlink', name='date', field=models.DateField(blank=True, null=True, help_text='Publication or event date.')),
        migrations.AddField(model_name='peopleresearchlink', name='location', field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name='peopleresearchlink', name='authors', field=models.TextField(blank=True, help_text='Authors in credited order, including external collaborators.')),
        migrations.AddField(model_name='peopleresearchlink', name='venue', field=models.CharField(blank=True, max_length=255, help_text='Conference, event, or journal name.')),
        migrations.AddField(model_name='peopleresearchlink', name='doi', field=models.CharField(blank=True, max_length=255, verbose_name='DOI')),
        migrations.AddField(model_name='peopleresearchlink', name='description', field=models.TextField(blank=True, help_text='Optional abstract or summary.')),
    ]
