from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class PeopleResearchLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeopleResearchLink
        fields = ['id', 'title', 'category', 'url', 'date', 'location', 'authors', 'venue', 'doi', 'description']


class PeopleSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)
    research_links = PeopleResearchLinkSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()  # Use a custom field
    full_title_name = serializers.SerializerMethodField()  # Add this field
    class Meta:
        model = People
        fields = [
            'id', 'title', 'full_name', 'full_title_name', 'association', 'image',
            'slug', 'created_at', 'updated_at', 'tags', 'research_links'
        ]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]  # Return only tag names

    def get_full_title_name(self, obj):
        """Return the full name with the title."""
        title = obj.title if obj.title else ""  # Ensure title is not None
        name = obj.full_name if obj.full_name else ""  # Ensure full_name is not None
        return f"{title} {name}".strip()  # Concatenate title and full name

# get people information based on the people slug
class PeopleInformationSerializer(serializers.ModelSerializer):
    research_links = PeopleResearchLinkSerializer(source='people.research_links', many=True, read_only=True)
    people = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    homepage_url = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    research_interests = serializers.SerializerMethodField()
    areas_of_expertise = serializers.SerializerMethodField()
    key_initiatives = serializers.SerializerMethodField()
    research_areas = serializers.SerializerMethodField()
    qualifications = serializers.SerializerMethodField()
    memberships = serializers.SerializerMethodField()
    role_badge = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = PeopleInformation
        fields = [
            'id', 'people', 'slug', 'full_name', 'image', 'research_interests',
            'areas_of_expertise', 'key_initiatives',
            'research_areas', 'qualifications',
            'role_badge', 'about_user', 'institution',
            'memberships', 'social_links',  # Include social_links
            'created_at', 'updated_at', 'email', 'homepage_url', 'research_links'
        ]

    def get_email(self, obj):
        if obj.people:
            for link in obj.people.social_links.all():
                if link.platform.name.lower() == "email":
                    return link.url
        return None

    def get_homepage_url(self, obj):
        if obj.people:
            for link in obj.people.social_links.all():
                if link.platform.name.lower() == "homepage":
                    return link.url
        return None


    def get_people(self, obj):
        """Return the full name of the related person."""
        return obj.people.full_name if obj.people else None

    def get_full_name(self, obj):
        """Return the full name of the related person."""
        title = obj.people.title if obj.people.title else ""  # Ensure title is not None
        name = obj.people.full_name if obj.people.full_name else ""  # Ensure full_name is not None
        return f"{title} {name}".strip()  # Concatenate title and full name

    def get_slug(self, obj):
        """Return the slug of the related person."""
        return obj.people.slug if obj.people else None

    def get_image(self, obj):
        """Return the image URL of the related person."""
        return obj.people.image.url if obj.people and obj.people.image else None

    def get_social_links(self, obj):
        """Fetch all social links for the associated person."""
        if obj.people:  # Ensure the People object exists
            return [
                {
                    "name": link.platform.name,
                    "icon": link.platform.icon or "",
                    "url": link.url
                }
                for link in obj.people.social_links.all() if link.platform.name.lower() not in ['homepage','email'] # Use related_name to fetch links
            ]
        return []

    def get_research_interests(self, obj):
        """Return a list of research interests."""
        return [interest.name for interest in obj.research_interests.all()]

    def get_areas_of_expertise(self, obj):
        """Return a list of areas of expertise."""
        return [area.name for area in obj.areas_of_expertise.all()]

    def get_key_initiatives(self, obj):
        """Return a list of key initiatives."""
        return [{
            "name": initiative.title,
            "url": initiative.url
            }
            for initiative in obj.key_initiatives.all()
            ]

    def get_research_areas(self, obj):
        """Return a list of key research areas."""
        return [{
            "name": area.title,
            "description": area.description
        }
        for area in obj.key_research_areas.all()
        ]

    def get_qualifications(self, obj):
        """Return a list of qualifications."""
        return [qualification.title for qualification in obj.qualifications.all()]

    def get_memberships(self, obj):
        """Return a list of memberships."""
        return [membership.title for membership in obj.memberships.all()]

    def get_role_badge(self, obj):
        """Return a list of role badges."""
        return [badge.name for badge in obj.role_badge.all()]
