from django import template
from risk.models import Riskmatrix
from django.utils.html import mark_safe
from django import forms
from django.urls import reverse
from datetime import date


register = template.Library()

@register.simple_tag(takes_context=True)
def _get_risk(context):
	riskmatrix = context.get('riskmatrix', None)
	test = dict(Riskmatrix.ASSESSMENT_CHOICES)
	advisory = context.get('advisory', None).content_object
	assessment_list = context.get('assessment_list', {})
	filter_date = date.today()
	for assessment in assessment_list:
		if assessment.advisory.content_object == advisory and assessment.consequence>=0 and assessment.probability>=0:
			if not assessment.mitigated_date or assessment.mitigated_date <= filter_date:
				return riskmatrix[str(assessment.consequence)][str(assessment.probability)]['value']
			else:
				return 0
	return -10

@register.simple_tag(takes_context=True)
def get_risk(context):
	riskmatrix = context.get('riskmatrix', None)
	test = dict(Riskmatrix.ASSESSMENT_CHOICES)
	advisory = context.get('advisory', None).content_object
	assessment_list = context.get('assessment_list', {})
	for assessment in assessment_list:
		if assessment.advisory.content_object == advisory and assessment.consequence>=0 and assessment.probability>=0:
			return test[riskmatrix[str(assessment.consequence)][str(assessment.probability)]['value']]
	return ""

@register.simple_tag(takes_context=True)
def get_matrix_class(context, obj):
	riskcolors = context.get('riskcolors', None)
	test = dict(Riskmatrix.ASSESSMENT_CHOICES)
	if obj and int(obj) in test:
		return riskcolors[str(obj)]['class']
	else:
		return ""

@register.simple_tag(takes_context=True)
def get_matrix_class_from_name(context, obj):
	riskcolors = context.get('riskcolors', None)
	test = dict(Riskmatrix.ASSESSMENT_CHOICES)
	if obj:
		for value, name in test.iteritems():
			if obj == name:
				return riskcolors[str(value)]['class']
	else:
		return ""
		
@register.simple_tag(takes_context=True)
def get_risk_class(context):
	riskcolors = context.get('riskcolors', None)
	riskmatrix = context.get('riskmatrix', None)
	advisory = context.get('advisory', None).content_object
	assessment_list = context.get('assessment_list', {})
	for assessment in assessment_list:
		if assessment.advisory.content_object == advisory and assessment.consequence>=0 and assessment.probability>=0:
			return riskcolors[str(riskmatrix[str(assessment.consequence)][str(assessment.probability)]['value'])]['class']

@register.simple_tag(takes_context=True)
def get_consequence_class(context):
	riskcolors = context.get('riskcolors', None)
	advisory = context.get('advisory', None).content_object
	assessment_list = context.get('assessment_list', {})
	for assessment in assessment_list:
		if assessment.advisory.content_object == advisory:
			return riskcolors[str(assessment.consequence)]['class']
	return ""

@register.simple_tag(takes_context=True)
def get_probability_class(context):
	riskcolors = context.get('riskcolors', None)
	advisory = context.get('advisory', None).content_object
	assessment_list = context.get('assessment_list', {})
	for assessment in assessment_list:
		if assessment.advisory.content_object == advisory:
			return riskcolors[str(assessment.probability)]['class']
	return ""
	
			
@register.simple_tag(takes_context=True)
def get_consequence(context):
	advisory = context.get('advisory', None).content_object
	assessment_list = context.get('assessment_list', {})
	customer = context.get('customer', None)
	for assessment in assessment_list:
		if assessment.advisory.content_object == advisory:
			return mark_safe("<a href=\"%s\">%s</a>" % (reverse('assessment:detail', kwargs={'pk': assessment.id}), assessment.get_consequence_display()))
	if customer:
		return mark_safe("<a href=\"%s?customer=%s&advisory=%s\">new</a>" % (reverse('assessment:add', kwargs={}), customer.id, advisory.id))
	else:
		return ""

@register.simple_tag(takes_context=True)
def get_probability(context):
	advisory = context.get('advisory', None).content_object
	assessment_list = context.get('assessment_list', {})
	customer = context.get('customer', None)
	for assessment in assessment_list:
		if assessment.advisory.content_object == advisory:
			return mark_safe("<a href=\"%s\">%s</a>" % (reverse('assessment:detail', kwargs={'pk': assessment.id}), assessment.get_probability_display()))
	if customer:
		return mark_safe("<a href=\"%s?customer=%s&advisory=%s\">new</a>" % (reverse('assessment:add', kwargs={}), customer.id, advisory.id))
	else:
		return ""
