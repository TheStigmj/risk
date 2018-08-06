# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
#from django.utils.encoding import force_unicode

from risk.models import Customer
import logging
	
class CustomerSelectForm(forms.Form):
	#customer = forms.ChoiceField(widget=forms.Select, choices=[ (o.id, str(o)) for o in Customer.objects.all()])
	#customer = forms.ChoiceField(widget=forms.Select, choices=Customer.objects.all().values_list('id', 'customer_name').order_by('id'), initial=2)
	#customer = forms.ChoiceField(widget=forms.Select)
	#customer = forms.ModelChoiceField(queryset=Customer.objects.all())

	def __init__(self, *args, **kwargs):
		"""If no initial data, provide some defaults."""
		kwargs['initial'] = kwargs.get('initial', {})
		super(CustomerSelectForm, self).__init__(*args, **kwargs)
		self.fields['customer'] = forms.ModelChoiceField(queryset=Customer.objects.all(), initial=kwargs['initial'], widget=forms.Select(attrs={'class':'form-control'}), required=False,)
