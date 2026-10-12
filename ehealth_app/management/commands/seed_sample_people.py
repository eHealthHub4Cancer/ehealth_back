"""Populate SQLite with complete, explicitly fictional profile records."""
from datetime import date, datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils.html import format_html

from ehealth_app.models import (
    People, PeopleTitle, PeopleInformation, PeopleResearchLink, Tag,
    ResearchInterest, AreaOfExpertise, KeyInitiatives, KeyResearchArea,
    Qualification, Membership, roleBadge, SocialPlatform, PeopleSocialLink, FileUpload,
)


PROFILES = [
    ('Amara Okafor', 'Dr.', 'Cancer genomics', 'Dublin', 'Genomic biomarkers', 'Molecular Biology'),
    ('Luca Moretti', 'Prof.', 'Clinical informatics', 'Cork', 'Electronic health records', 'Health Informatics'),
    ('Sofia Lindholm', 'Dr.', 'Biomedical imaging', 'Galway', 'Medical image analysis', 'Biomedical Engineering'),
    ('Ethan Mercer', 'Assoc. Prof.', 'Federated learning', 'Limerick', 'Privacy-preserving analytics', 'Computer Science'),
    ('Priya Nair', 'Dr.', 'Population health', 'Belfast', 'Cancer outcomes', 'Epidemiology'),
    ('Mateo Silva', 'Dr.', 'Precision medicine', 'Dublin', 'Treatment response modelling', 'Biostatistics'),
    ('Hana Sato', 'Prof.', 'Digital pathology', 'Cork', 'Tissue classification', 'Computational Pathology'),
    ('Nadia Farouk', 'Dr.', 'Patient engagement', 'Galway', 'Patient-reported outcomes', 'Health Psychology'),
    ('Oliver Byrne', 'Dr.', 'Data interoperability', 'Limerick', 'Clinical terminology mapping', 'Data Science'),
    ('Elena Petrova', 'Assoc. Prof.', 'Cancer therapeutics', 'Belfast', 'Drug discovery', 'Pharmacology'),
]


class Command(BaseCommand):
    help = 'Create 10 fictional researchers with complete profiles and 40 research outputs in SQLite.'

    @transaction.atomic
    def handle(self, *args, **options):
        if connection.vendor != 'sqlite':
            raise CommandError('Sample data is restricted to SQLite. Run with --test.')
        created_people = created_outputs = 0
        for index, (name, title_name, topic, city, focus, degree) in enumerate(PROFILES, start=1):
            slug = 'sample-' + name.lower().replace(' ', '-')
            base_url = f'https://example.org/fictional-research/{slug}'
            institute = f'{city} Institute for Digital Cancer Research (fictional)'
            title, _ = PeopleTitle.objects.get_or_create(name=title_name)
            person, created = People.objects.get_or_create(slug=slug, defaults={
                'title': title, 'full_name': name,
                'association': f'{topic} researcher, {institute}',
                'image': f'people_images/samples/{slug}.png',
            })
            created_people += int(created)
            self.create_avatar(slug, name, index)
            person.tags.add(*(Tag.objects.get_or_create(name=tag)[0]
                              for tag in ['Fictional sample', 'Researcher', city]))
            info, _ = PeopleInformation.objects.get_or_create(people=person, defaults={
                'institution': institute,
                'about_user': str(format_html(
                    '<p><strong>Fictional profile for local testing.</strong></p>'
                    '<h3>Biography</h3><p>{} researches {} at {}. Their work explores {} '
                    'and collaborative approaches to digital cancer research.</p>'
                    '<h3>Current work</h3><p>This sample profile describes a project combining '
                    'clinical data analysis, reproducible methods, and patient-centred evaluation.</p>',
                    name, topic.lower(), institute, focus.lower(),
                )),
            })
            for field, model, values in [
                ('research_interests', ResearchInterest, [topic, focus, 'Digital health']),
                ('areas_of_expertise', AreaOfExpertise, [focus, 'Research methodology', 'Data analysis']),
                ('role_badge', roleBadge, ['Researcher', 'Fictional sample', city]),
            ]:
                getattr(info, field).add(*(model.objects.get_or_create(name=value)[0] for value in values))
            info.qualifications.add(*(Qualification.objects.get_or_create(title=value)[0] for value in [
                f'PhD in {degree}, {institute} (fictional)',
                f'MSc in {degree}, Sample Graduate Academy (fictional)',
            ]))
            info.memberships.add(Membership.objects.get_or_create(
                title='Digital Cancer Research Society — fictional membership',
            )[0])
            info.key_research_areas.add(KeyResearchArea.objects.get_or_create(title=f'{focus} (sample)', defaults={
                'description': f'Fictional programme investigating {focus.lower()} through collaborative digital health methods.',
            })[0])
            info.key_initiatives.add(KeyInitiatives.objects.get_or_create(
                title=f'{topic} collaboration (fictional)', url=f'{base_url}/initiative',
            )[0])
            for platform_name, icon, url in [
                ('Homepage', 'language', base_url),
                ('Email', 'mail', f'{slug.removeprefix("sample-")}@example.org'),
                ('Research profile', 'school', f'{base_url}/profile'),
                ('Code repository', 'code', f'{base_url}/code'),
            ]:
                platform, _ = SocialPlatform.objects.get_or_create(name=platform_name, defaults={'icon': icon})
                PeopleSocialLink.objects.get_or_create(people=person, platform=platform, url=url)
            for position, category in enumerate(PeopleResearchLink.Category.values):
                output_slug = f'{slug}-{category}'
                output_date = date(2025, ((index + position - 1) % 12) + 1, 10 + position)
                output_url = f'{base_url}/{category}'
                output, output_created = PeopleResearchLink.objects.get_or_create(
                    people=person, category=category, url=output_url, defaults={
                        'title': f'{focus}: {category.title()} study (fictional)',
                        'date': output_date, 'location': f'{city}, Ireland',
                        'authors': f'{name}; {PROFILES[index % len(PROFILES)][0]}',
                        'venue': 'Journal of Sample Digital Health (fictional)' if category == 'publication'
                                 else 'Sample Digital Cancer Research Symposium (fictional)',
                        'doi': f'10.0000/fictional.{index:02d}.{category}',
                        'description': f'Fictional {category} describing methods and findings for {focus.lower()}. '
                                       'All authorship, event details, DOI values, and links are sample data.',
                        'position': position,
                    },
                )
                created_outputs += int(output_created)
                FileUpload.objects.get_or_create(slug=output_slug, defaults={
                    'filename': f'{output_slug}.pdf', 'url': output_url, 'is_public': True,
                    'embargo_until': datetime(2025, 1, 1, tzinfo=timezone.utc if settings.USE_TZ else None),
                })
        self.stdout.write(self.style.SUCCESS(
            f'Created {created_people} fictional people and {created_outputs} research outputs. '
            'Existing records preserved. All 10 sample profiles are available in SQLite.'
        ))

    def create_avatar(self, slug, name, index):
        path = Path(settings.MEDIA_ROOT) / 'people_images' / 'samples' / f'{slug}.png'
        if path.exists():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        palette = ['#155e75', '#6d28d9', '#047857', '#b45309', '#be185d']
        image = Image.new('RGB', (320, 320), palette[(index - 1) % len(palette)])
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=100)
        initials = ''.join(part[0] for part in name.split())
        draw.text((160, 160), initials, fill='white', font=font, anchor='mm')
        image.save(path)
