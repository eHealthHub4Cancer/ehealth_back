from django import forms

from .models import People


class PeopleAdminForm(forms.ModelForm):
    class Meta:
        model = People
        fields = '__all__'
        help_texts = {
            'image': 'Large JPEG, PNG, and WebP portraits are resized in your browser before upload. '
                     'The uploaded image must be 5 MB or smaller. Animated images are not resized.',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        # Validate only a new upload, not an existing stored portrait.
        if 'image' in self.files and image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                'This image is too large. Choose an image of 5 MB or smaller, '
                'or use a JPEG, PNG, or WebP portrait so your browser can resize it.'
            )
        return image
