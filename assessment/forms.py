# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
#from django.utils.encoding import force_unicode

from itertools import chain
from django.utils.html import conditional_escape
from django.utils.safestring import SafeData, SafeText, mark_safe
from django.urls import reverse
from risk.models import Customer,Product,Assessment
import logging
	
#class CustomerSelectForm(forms.Form):
#	#customer = forms.ChoiceField(widget=forms.Select, choices=[ (o.id, str(o)) for o in Customer.objects.all()])
#	#customer = forms.ChoiceField(widget=forms.Select, choices=Customer.objects.all().values_list('id', 'customer_name').order_by('id'), initial=2)
#	#customer = forms.ChoiceField(widget=forms.Select)
#	#customer = forms.ModelChoiceField(queryset=Customer.objects.all())
#
#	def __init__(self, *args, **kwargs):
#		"""If no initial data, provide some defaults."""
#		kwargs['initial'] = kwargs.get('initial', {})
#		super(CustomerSelectForm, self).__init__(*args, **kwargs)
#		self.fields['customer'] = forms.ModelChoiceField(queryset=Customer.objects.all(), initial=kwargs['initial'], required=False,)
	
class AssessmentEditForm(forms.ModelForm):

	#def __init__(self, *args, **kwargs):
	#	"""If no initial data, provide some defaults."""
	#	initial = kwargs.get('initial', {})
	#	#initial['blacklist'] = self.object.blacklist
	#	kwargs['initial'] = initial
	#	customer = kwargs.pop('customer', 1)
	#	super(AssessmentEditForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Assessment
		fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action_description','consequence_after_action','probability_after_action','mitigated_date']
		#fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action']
		widgets = {
			'mitigated_date': forms.DateTimeInput(attrs={'class': 'datetime-input'})
		}

class AssessmentAddForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		"""If no initial data, provide some defaults."""
		initial = kwargs.get('initial', {})
		#initial['blacklist'] = self.object.blacklist
		kwargs['initial'] = initial
		customer = kwargs.pop('customer', 1)
		super(AssessmentAddForm, self).__init__(*args, **kwargs)
		self.fields['advisory'].initial = kwargs['initial']['advisory']
		self.fields['customer'].initial = kwargs['initial']['customer']

	class Meta:
		model = Assessment
		fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action_description','consequence_after_action','probability_after_action','mitigated_date']
		widgets = {
			'mitigated_date': forms.DateTimeInput(attrs={'class': 'datetime-input'})
		}
		#fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action']
