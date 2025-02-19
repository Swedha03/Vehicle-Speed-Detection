from django import forms
from django.core.exceptions import ValidationError

class VideoUploadForm(forms.Form):
    video = forms.FileField(
        label='Select a video file',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    def clean_video(self):
        video = self.cleaned_data.get('video')

        # Restrict file types to certain video formats
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        if not video.name.endswith(tuple(valid_extensions)):
            raise ValidationError(f'Invalid file type. Allowed formats: {", ".join(valid_extensions)}.')

        # Restrict file size (example: max size 50MB)
        max_size_in_mb = 50
        if video.size > max_size_in_mb * 1024 * 1024:
            raise ValidationError(f'File size exceeds {max_size_in_mb}MB.')

        return video
