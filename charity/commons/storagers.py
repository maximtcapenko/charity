from django.conf import settings
from django.core.files.storage import FileSystemStorage


private = FileSystemStorage(location= '%s/%s' % (settings.BASE_DIR, 'private'))