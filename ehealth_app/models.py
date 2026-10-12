from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

# Tag model
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PeopleTitle(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# People model
class People(models.Model):
    title = models.ForeignKey(
        PeopleTitle, on_delete=models.PROTECT, blank=True, null=True, related_name='people',
    )
    full_name = models.CharField(max_length=100)
    association = models.TextField()
    image = models.ImageField(upload_to='people_images/', blank=True, null=True)  # Add image field
    slug = models.SlugField(unique=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)  # Add tags as a ManyToManyField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.full_name)
        super(People, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title or ''} {self.full_name}".strip()
    
class PeopleResearchLink(models.Model):
    """A named research output linked from a person's profile."""

    class Category(models.TextChoices):
        PUBLICATION = 'publication', 'Publication'
        POSTER = 'poster', 'Poster'
        PRESENTATION = 'presentation', 'Presentation'
        OTHER = 'other', 'Other'

    people = models.ForeignKey(People, on_delete=models.CASCADE, related_name='research_links')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.PUBLICATION)
    url = models.URLField(max_length=2000)
    date = models.DateField(blank=True, null=True, help_text='Publication or event date.')
    location = models.CharField(max_length=255, blank=True)
    authors = models.TextField(blank=True, help_text='Authors in credited order, including external collaborators.')
    venue = models.CharField(max_length=255, blank=True, help_text='Conference, event, or journal name.')
    doi = models.CharField(max_length=255, blank=True, verbose_name='DOI')
    description = models.TextField(blank=True, help_text='Optional abstract or summary.')
    position = models.PositiveIntegerField(default=0, help_text='Lower numbers appear first.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return self.title


class ResearchInterest(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class SocialPlatform(models.Model):
    """Model to define social platforms dynamically."""
    name = models.CharField(max_length=50, unique=True)  # e.g., Twitter, LinkedIn
    icon = models.CharField(max_length=100, blank=True, null=True)  # Optional: for storing platform icons or classes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class PeopleSocialLink(models.Model):
    """Model to define social links for specific people."""
    people = models.ForeignKey(People, on_delete=models.CASCADE, related_name='social_links')
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE, related_name='links')  # Dynamic platform
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('people', 'platform', 'url')  # Prevent duplicates

    def __str__(self):
        return f"{self.platform.name} - {self.url}"

class AreaOfExpertise(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class roleBadge(models.Model):
    """Model for role badges."""
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class KeyInitiatives(models.Model):
    """Model for key initiatives."""
    title = models.CharField(max_length=200)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class KeyResearchArea(models.Model):
    """Model for key research areas."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Qualification(models.Model):
    """Model for qualifications."""
    title = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"

class Membership(models.Model):
    """Model for memberships."""
    title = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"
    
class PeopleInformation(models.Model):
    """Model for detailed information about a person."""
    people = models.ForeignKey('People', on_delete=models.CASCADE)
    about_user = RichTextField()
    institution = models.TextField(null=True)
    research_interests = models.ManyToManyField(ResearchInterest, blank=True)  # Add multiple research interests
    areas_of_expertise = models.ManyToManyField(AreaOfExpertise, blank=True)  # Add multiple areas of expertise
    key_initiatives = models.ManyToManyField(KeyInitiatives, blank=True)  # Add multiple key initiatives
    key_research_areas = models.ManyToManyField(KeyResearchArea, blank=True)  # Add multiple key research areas
    qualifications = models.ManyToManyField(Qualification, blank=True)  # Add multiple qualifications
    memberships = models.ManyToManyField(Membership, blank=True)  # Add multiple memberships
    role_badge = models.ManyToManyField(roleBadge, blank=True)  # Add multiple role badges
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.people.full_name
    
class FileUpload(models.Model):
    """Model for file metadata referencing an external URL (instead of uploading a file)."""
    url = models.URLField(blank=False, default="https://example.com")
    filename = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    is_public = models.BooleanField(default=True)
    embargo_until = models.DateTimeField(blank=True, null=True, help_text="Keep private until this date/time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug from filename if not provided
        if not self.slug:
            self.slug = slugify(self.filename)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.filename} ({'Public' if self.is_public else 'Private'})"

    class Meta:
        ordering = ['-created_at']
