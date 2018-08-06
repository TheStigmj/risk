# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
#from django.utils.encoding import force_unicode

from itertools import chain
from django.utils.html import conditional_escape
from django.utils.safestring import SafeData, SafeText, mark_safe
from django.urls import reverse
from risk.models import Customer,Product,Userprofile
import logging

class CustomerEditForm2(forms.Form):
	#customer = forms.ChoiceField(widget=forms.Select, choices=[ (o.id, str(o)) for o in Customer.objects.all()])
	#customer = forms.ChoiceField(widget=forms.Select, choices=Customer.objects.all().values_list('id', 'customer_name').order_by('id'), initial=2)
	#customer = forms.ChoiceField(widget=forms.Select)
	#customer = forms.ModelChoiceField(queryset=Customer.objects.all())

	def __init__(self, *args, **kwargs):
		"""If no initial data, provide some defaults."""
		kwargs['initial'] = kwargs.get('initial', {})
		super(CustomerEditForm2, self).__init__(*args, **kwargs)
		#self.fields['blacklist'] = forms.MultipleChoiceField(widget=forms.widgets.CheckboxSelectMultiple, choices=Product.objects.all().values_list('id','product_name').order_by('product_name'), initial=kwargs['initial'])
		self.fields['blacklist'] = forms.MultipleChoiceField(widget=forms.widgets.CheckboxSelectMultiple, choices=[(p.pk,p.product_name) for p in Product.objects.all().order_by('product_name')], initial=kwargs['initial'])


class MyCheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([v for v in value])
        for i, (option_value, option_label) in enumerate(sorted(chain(self.choices, choices), key=lambda x: x[1])):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.widgets.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            #option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            #option_label = conditional_escape(force_unicode(option_label))
            option_label = conditional_escape(option_label)
            output.append(u'<li><label%s>%s <a href="%s">%s</a></label></li>' % (label_for, rendered_cb, reverse("product:detail", kwargs={"pk": option_value}), option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))
		
class UserprofileEditForm(forms.ModelForm):

	#def __init__(self, *args, **kwargs):
	#	"""If no initial data, provide some defaults."""
	#	initial = kwargs.get('initial', {})
	#	#initial['blacklist'] = self.object.blacklist
	#	kwargs['initial'] = initial
	#	customer = kwargs.pop('customer', 1)
	#	super(AssessmentEditForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Userprofile
		fields = ['wlnotify','wlemail','wlsms']
		#fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action']
		#widgets = {
		#	'mitigated_date': forms.DateTimeInput(attrs={'class': 'datetime-input'})
		#}

class UserprofileAddForm(forms.ModelForm):

#	def __init__(self, *args, **kwargs):
#		"""If no initial data, provide some defaults."""
#		initial = kwargs.get('initial', {})
#		#initial['blacklist'] = self.object.blacklist
#		kwargs['initial'] = initial
#		customer = kwargs.pop('customer', 1)
#		super(ProfileAddForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Userprofile
		fields = ['wlnotify','wlemail','wlsms']
		#fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action']
