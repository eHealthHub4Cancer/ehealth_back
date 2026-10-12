from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import (
    Tag, People, PeopleInformation, 
    ResearchInterest, SocialPlatform, 
    PeopleSocialLink, AreaOfExpertise,
    KeyInitiatives, KeyResearchArea,
    Qualification, Membership,
    roleBadge, FileUpload, PeopleResearchLink, PeopleTitle
)

# Tag admin
@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'created_at')  # Display name and created date
    search_fields = ['name']  # Enable search for tags by name
    ordering = ['name']  # Order tags alphabetically


class PeopleResearchLinkInline(StackedInline):
    model = PeopleResearchLink
    fields = ('title', 'category', 'url', 'date', 'venue', 'location', 'authors', 'doi', 'description', 'position')
    extra = 0


@admin.register(PeopleResearchLink)
class PeopleResearchLinkAdmin(ModelAdmin):
    list_display = ('title', 'people', 'category', 'position')
    list_filter = ('category',)
    search_fields = ('title', 'people__full_name', 'url')
    autocomplete_fields = ('people',)


@admin.register(PeopleTitle)
class PeopleTitleAdmin(ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)


class PeopleSocialLinkInline(StackedInline):
    model = PeopleSocialLink
    fields = ('platform', 'url')
    autocomplete_fields = ('platform',)
    extra = 0


# People admin
@admin.register(People)
class PeopleAdmin(ModelAdmin):
    inlines = [PeopleSocialLinkInline, PeopleResearchLinkInline]
    list_display = ('full_name', 'title', 'created_at')  # Display main fields
    search_fields = ('full_name',)  # Enable search for people's names
    autocomplete_fields = ['tags', 'title']  # Enable autocomplete for tags
    prepopulated_fields = {'slug': ('full_name',)}  # Automatically generate slugs
    list_filter = ('title', 'created_at')  # Add filters for title and creation date
    ordering = ['full_name']  # Order by full name
    filter_horizontal = ['tags']  # Add horizontal filter for tags


# PeopleInformation admin
@admin.register(PeopleInformation)
class PeopleInformationAdmin(ModelAdmin):
    list_display = ('people', 'created_at', 'updated_at')  # Display related person and timestamps
    search_fields = ('people__full_name',)  # Enable search for people's names
    autocomplete_fields = ['people', 'research_interests', 
                           'areas_of_expertise', 'key_initiatives',
                           'key_research_areas', 'qualifications', 
                           'memberships', 'role_badge']  # Enable autocomplete for the related person
    readonly_fields = ('created_at', 'updated_at')  # Make timestamps read-only

# ResearchInterest admin
@admin.register(ResearchInterest)
class ResearchInterestAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')  # Display name and timestamps
    search_fields = ['name']
    ordering = ['name']

# SocialPlatform admin
@admin.register(SocialPlatform)
class SocialPlatformAdmin(ModelAdmin):
    list_display = ('name', 'icon', 'created_at', 'updated_at')
    search_fields = ['name']
    ordering = ['name']

# AreaOfExpertise admin
@admin.register(AreaOfExpertise)
class AreaOfExpertiseAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ['name']
    ordering = ['name']

# PeopleSocialLink admin
@admin.register(PeopleSocialLink)
class PeopleSocialLinkAdmin(ModelAdmin):
    list_display = ('people', 'platform', 'url', 'created_at')
    search_fields = ('people__full_name', 'platform__name', 'url')
    list_filter = ('platform', 'created_at')
    autocomplete_fields = ['people', 'platform']

# KeyInitiatives admin
@admin.register(KeyInitiatives)
class KeyInitiativesAdmin(ModelAdmin):
    list_display = ('title', 'url', 'created_at', 'updated_at')
    search_fields = ['title', 'url']
    ordering = ['title']

# KeyResearchArea admin
@admin.register(KeyResearchArea)
class KeyResearchAreaAdmin(ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ['title']
    ordering = ['title']

# Qualification admin
@admin.register(Qualification)
class QualificationAdmin(ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ['title']
    ordering = ['title']

# Membership admin
@admin.register(Membership)
class MembershipAdmin(ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ['title']
    ordering = ['title']

# roleBadge admin
@admin.register(roleBadge)
class roleBadgeAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ['name']
    ordering = ['name']

@admin.register(FileUpload)
class FileUploadAdmin(ModelAdmin):
    list_display = ('filename', 'is_public', 'embargo_until', 'created_at', 'updated_at')
    search_fields = ('filename', 'slug')
    list_filter = ('is_public', 'embargo_until')
    prepopulated_fields = {'slug': ('filename',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['created_at']


# Apply the same theme to Django's user and group management screens.
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
