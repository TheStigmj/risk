from django import template
from risk.models import Riskmatrix
from django.utils.html import mark_safe
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def get_risk(context, consequence, probability):
	riskmatrix = context.get('riskmatrix', None)
	test = dict(Riskmatrix.ASSESSMENT_CHOICES)
	if riskmatrix and consequence and probability and int(consequence)>=0 and int(probability)>=0:
		return test[riskmatrix[str(consequence)][str(probability)]['value']]
	else:
		return ""

@register.simple_tag(takes_context=True)
def get_matrix_class(context, obj):
	riskcolors = context.get('riskcolors', None)
	test = dict(Riskmatrix.ASSESSMENT_CHOICES)
	if obj and riskcolors and obj in test:
		return riskcolors[str(obj)]['class']
	else:
		return ""
		
@register.simple_tag(takes_context=True)
def get_risk_class(context, consequence, probability):
	riskmatrix = context.get('riskmatrix', None)
	riskcolors = context.get('riskcolors', None)
	if riskcolors and riskmatrix and consequence and probability and int(consequence)>=0 and int(probability)>=0:
		risk = riskmatrix[str(consequence)][str(probability)]['value']
		return get_matrix_class(context, risk)
	else:
		return ""
	
@register.simple_tag(takes_context=True)
def get_customers(context):
	assessment = context.get('assessment', None)
	retval = []
	for customer in assessment.customer.all():
		retval.append("<a href=\"%s\">%s</a>" % (reverse("customer:detail", kwargs={'pk': customer.id}), customer.customer_name))
	return mark_safe(", ".join(retval))
	
@register.simple_tag(takes_context=True)
def get_watchlist_addlink(context):
	return ""
	