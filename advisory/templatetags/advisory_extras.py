from django import template
from django.contrib.contenttypes.models import ContentType
from risk.models import Ciscoadvisory

register = template.Library()

@register.assignment_tag
def content_type(obj):
	if not obj:
		return False
	return ContentType.objects.get_for_model(obj)
	
@register.simple_tag
def lookup_content_type(obj):
	if not obj:
		return ""
	if str(obj) == 'ciscoadvisory':
		return "Cisco"
	else:
		return obj