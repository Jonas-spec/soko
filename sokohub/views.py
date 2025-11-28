# sokohub/views.py
from django.conf import settings
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required  # optional protection

@staff_member_required  # only staff/admin can view
def debug_templates(request):
    # settings.TEMPLATES is a list of template engine configs (each has 'DIRS')
    template_dirs = settings.TEMPLATES
    return render(request, 'debug_templates.html', {'template_dirs': template_dirs})
