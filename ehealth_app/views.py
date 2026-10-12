from django.shortcuts import render
from rest_framework import viewsets, generics
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponseNotFound

from .serializers import (
    TagSerializer,
    PeopleSerializer,
    PeopleInformationSerializer
)
from rest_framework.exceptions import NotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import (
    Tag, People, PeopleInformation, 
    ResearchInterest, SocialPlatform, 
    PeopleSocialLink, AreaOfExpertise, 
    KeyInitiatives, KeyResearchArea, 
    Qualification, Membership, FileUpload
)
from django.contrib.auth.decorators import login_required

# Create your views here.
class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    ordering_fields = ['name']

class PeopleListView(generics.ListAPIView):
    queryset = People.objects.select_related('title').prefetch_related('tags', 'research_links')
    serializer_class = PeopleSerializer
    ordering_fields = ['full_name']
    # order by date created
    ordering = ['-created_at']

class PeopleInformationListView(generics.RetrieveAPIView):
    queryset = PeopleInformation.objects.all()
    serializer_class = PeopleInformationSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    # order by date created
    ordering = ['-created_at']

    def get_object(self):
        slug = self.kwargs.get('slug')
        try:
            return self.get_queryset().select_related('people', 'people__title').prefetch_related(
                'people__research_links'
            ).get(people__slug=slug)
        except PeopleInformation.DoesNotExist:
            raise NotFound(f"No PeopleInformation found for slug: {slug}")
        
class PeopleInformationAllView(generics.ListAPIView):  # Changed to ListAPIView
    queryset = PeopleInformation.objects.all()
    serializer_class = PeopleInformationSerializer
    ordering = ['-created_at']  # Order by creation date, newest first

    def get_queryset(self):
        # Optionally, you can add filtering or additional logic here
        return PeopleInformation.objects.all().select_related('people', 'people__title').prefetch_related(
            'research_interests',
            'areas_of_expertise',
            'key_initiatives',
            'key_research_areas',
            'qualifications',
            'memberships',
            'role_badge',
            'people__social_links',
            'people__research_links'
        )

def home(request):
    return render(request, 'htmls/index.html')

def view_document(request):
    return render(request, 'htmls/docs.html')

@login_required(login_url='/e_admin/login/')
def view_files(request):
    # Get all files
    # Get all files
    files = FileUpload.objects.all()
    
    # Handle search
    search_query = request.GET.get('q', '')
    if search_query:
        files = files.filter(filename__icontains=search_query)
    
    # Handle sorting
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'filename':
        files = files.order_by('filename')
    elif sort_by == 'is_public':
        files = files.order_by('-is_public')
    else:  # Default to latest
        files = files.order_by('-created_at')
    
    # Handle dynamic page size
    default_limit = 10
    limit = int(request.GET.get('limit', default_limit))
    if limit < default_limit:
        limit = default_limit
    
    paginator = Paginator(files, limit)
    page = request.GET.get('page', 1)
    try:
        files_paginated = paginator.page(page)
    except PageNotAnInteger:
        files_paginated = paginator.page(1)
    except EmptyPage:
        files_paginated = paginator.page(paginator.num_pages)
    
    # Get username for greeting
    username = request.user.username if request.user.is_authenticated else 'Guest'
    
    context = {
        'files': files_paginated,
        'search_query': search_query,
        'sort_by': sort_by,
        'username': username,
        'current_limit': limit,
        'has_more': files_paginated.has_next(),
        'default_limit': default_limit,
    }
    return render(request, 'htmls/files.html', context)

def file_view(request, slug):
    # Retrieve the file object by slug or return 404 if not found
    file_obj = get_object_or_404(FileUpload, slug=slug)
    
    # Check if the file is publicly accessible
    is_accessible = file_obj.is_public and (
        file_obj.embargo_until is None or file_obj.embargo_until <= timezone.now()
    )
    
    # Context for the template
    context = {
        'file_url': file_obj.url if is_accessible else None,
        'error_message': None if is_accessible else "This file is not accessible. Please check back later.",
        'logo_url': 'https://ehealth4cancer.eu/ehealth-logo.png'  # Replace with actual eHealth logo URL
    }
    
    return render(request, 'htmls/file_access.html', context)
