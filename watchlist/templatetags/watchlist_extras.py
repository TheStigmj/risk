from django import template
from django.utils.encoding import force_text, unquote
from django.utils.html import mark_safe
from django.contrib.admin.models import LogEntry

register = template.Library()

@register.simple_tag
def define(val=None):
	return val
  
@register.simple_tag
def get_log_entry(modelid, objid):
	try:
		last_action = LogEntry.objects.filter(
			object_id=objid,
			content_type=modelid
		).select_related().latest('action_time')
	except LogEntry.DoesNotExist:
		last_action = "n/a"
	return last_action

@register.simple_tag
def get_log_entry_with_user(modelid, objid):
	try:
		last_action = LogEntry.objects.filter(
			object_id=objid,
			content_type=modelid
		).select_related().latest('action_time')
	except LogEntry.DoesNotExist:
		last_action = '<span class="risk-cl-username">n/a</span> (<span class="risk-cl-logresume">n/a</span>)'
	if not isinstance(last_action, basestring):
		last_action = '<span class="risk-cl-username">%s</span> (<span class="risk-cl-logresume">%s</span>)' % (last_action.user.username, last_action)
	return mark_safe(last_action)
