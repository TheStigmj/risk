# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.http import HttpResponse

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse
from django.views import generic
from django.db.models import Subquery
from django_tables2 import RequestConfig
from risk.forms import CustomerSelectForm
from bootstrap3_datetime.widgets import DateTimePicker
from assessment.forms import AssessmentEditForm, AssessmentAddForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.utils.encoding import force_text

from risk.models import Advisory, Product, Customer, Assessment, Watchlist
import logging, json
import inspect, StringIO
def introspect(something):
	methods = inspect.getmembers(something, inspect.ismethod)
	others = inspect.getmembers(something, lambda x: not inspect.ismethod(x))
	retval = StringIO.StringIO()
	retval.write("\nVariables :\n")
	for name, value in others: retval.write(name + "=" + value + "\n")
	print
	retval.write("\n" + 'Methods:\n')
	for name, value in methods: retval.write(name + "=" + value + "\n")
	retval.write("\n")
	retval.seek(0)
	return retval.read()

from django.forms.models import modelform_factory
from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
import logging


class ModelFormWidgetMixin(object):
	def get_form_class(self):
		return modelform_factory(self.model, fields=self.fields, widgets=self.widgets)
	
class IndexView(LoginRequiredMixin, generic.ListView):
	template_name = 'assessment/index.html'
	_customer = None

	def get_queryset(self):
		#l = logging.getLogger('django.db.backends')
		#l.setLevel(logging.DEBUG)
		#l.addHandler(logging.StreamHandler())
		#First, let's get all advisories, reverse ordered by last_updated
		queryset = Assessment.objects.all().order_by('-modified_date')
		#Check if we are looking at a specific customer
		if self.request.GET.get("customer"):
			#Get the customer number
			cust = int(self.request.GET.get("customer"))
			#Assume the customer is valid
			ok = True
			try:
				# Try getting the customer information
				self._customer = Customer.objects.get(pk=cust)
			except Customer.DoesNotExist:
				# The customer does not exist, so we'll clear the queryset.
				queryset = None
				# And invalidate the choice for further processing here.
				ok = False
			# The customer was OK and we got some data.
			if ok:
				# Find the products the customer does NOT care about
				#products = self._customer.blacklist.all()
				# And filter out all others from the queryset
				queryset = queryset.filter(customer=self._customer)
		else:
			queryset = None
		
		return queryset
		
	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		
		# Are we looking at a specific customer?
		if self._customer:
			# Yes, so we'll add some contexts for use in the template
			#test = self._customer.riskmatrix.matrix
			#context['riskmatrix'].update({customer.id: json.loads(customer.riskmatrix.matrix)})
			context['riskmatrix'] = json.loads(self._customer.riskmatrix.matrix)
			context['riskcolors'] = json.loads(self._customer.riskmatrix.colors)
			context['customer'] = self._customer
			context['customer_id'] = self._customer.id
			# Get all assessments made for this customer
			#context['assessment_list'] = Assessment.objects.all().filter(customer=self._customer).prefetch_related('advisory')
			context['customer_selectform'] = CustomerSelectForm(initial={'customer': self._customer.id})
		else:
			context['customer_selectform'] = CustomerSelectForm()
		return context

	def get_form_kwargs(self):
		print "entering get_form_kwargs"
		kwargs = super().get_form_kwargs()
		print "in get_form_kwargs and self.request = %s" % (introspect(self.request))
		kwargs.update({'request': self.request})
		return kwargs

		
class DetailView(LoginRequiredMixin, generic.DetailView):
	model = Assessment
	template_name = 'assessment/detail.html'

	def get_context_data(self, **kwargs):
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		context['modelid'] = ContentType.objects.get_for_model(Assessment).id
		context['riskmatrix'] = json.loads(self.object.customer.riskmatrix.matrix)
		context['riskcolors'] = json.loads(self.object.customer.riskmatrix.colors)
		if self.request.user.is_authenticated:
			try:
				context['watchlist'] = Watchlist.objects.get(user=self.request.user, content_type=context['modelid'], object_id=self.object.id)
			except Watchlist.DoesNotExist:
				context['watchlist'] = None

		#context['bug_ids'] = self.object.bug_ids.all()
		#context['cves'] = self.object.cves.all()
		#context['cwe'] = self.object.cwe.all()
		#context['ips_signatures'] = self.object.ips_signatures.all()
		#context['products'] = self.object.product_names.all()
		return context

class DetailUpdateView(LoginRequiredMixin, ModelFormWidgetMixin, generic.edit.UpdateView):
	model = Assessment
	template_name = 'assessment/edit.html'
	#form_class = AssessmentEditForm
	fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action_description','consequence_after_action','probability_after_action','mitigated_date']
	widgets = {
		'mitigated_date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
			"calendarWeeks": True,
			"showTodayButton": True,
			}),
	}
	def log_addition(self, request, object, message):
		"""
		Log that an object has been successfully added.
	
		The default implementation creates an admin LogEntry object.
		"""
		from django.contrib.admin.models import LogEntry, ADDITION
		return LogEntry.objects.log_action(
			user_id=request.user.pk,
			content_type_id=get_content_type_for_model(object).pk,
			object_id=object.pk,
			object_repr=force_text(object),
			action_flag=ADDITION,
			change_message=message,
		)
	
	def log_change(self, request, object, message):
		"""
		Log that an object has been successfully changed.
	
		The default implementation creates an admin LogEntry object.
		"""
		from django.contrib.admin.models import LogEntry, CHANGE
		return LogEntry.objects.log_action(
			user_id=request.user.pk,
			content_type_id=get_content_type_for_model(object).pk,
			object_id=object.pk,
			object_repr=force_text(object),
			action_flag=CHANGE,
			change_message=message,
		)
	
	def log_deletion(self, request, object, object_repr):
		"""
		Log that an object will be deleted. Note that this method must be
		called before the deletion.
	
		The default implementation creates an admin LogEntry object.
		"""
		from django.contrib.admin.models import LogEntry, DELETION
		return LogEntry.objects.log_action(
			user_id=request.user.pk,
			content_type_id=get_content_type_for_model(object).pk,
			object_id=object.pk,
			object_repr=object_repr,
			action_flag=DELETION,
		)

	def get_context_data(self, **kwargs):
		context = super(generic.edit.UpdateView, self).get_context_data(**kwargs)
		
		return context
		
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(DetailUpdateView, self).post(request, *args, **kwargs)
	
	def form_valid(self, form):
		from django.contrib.admin.utils import construct_change_message
		change_message = construct_change_message(form, None, None)
		self.log_change(self.request, self.object, change_message)
		return super(DetailUpdateView, self).form_valid(form)
		
	def get_success_url(self):
		#self.form._set_choices(Product.objects.all().order_by('product_name').values('id', 'product_name'))
		return reverse('assessment:detail', kwargs={'pk': self.object.pk})
		
class DetailAddView(LoginRequiredMixin, ModelFormWidgetMixin, generic.edit.CreateView):
	model = Assessment
	template_name = 'assessment/edit.html'
	#form_class = AssessmentAddForm
	fields = ['valid','consequence','consequence_description','probability','probability_description','risk_description','action_description','consequence_after_action','probability_after_action','mitigated_date']
	#fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action']
	initial = {}
	widgets = {
		'mitigated_date': forms.DateTimeInput(attrs={'class': 'datetime-input'})
	}
	def log_addition(self, request, object, message):
		"""
		Log that an object has been successfully added.
	
		The default implementation creates an admin LogEntry object.
		"""
		from django.contrib.admin.models import LogEntry, ADDITION
		return LogEntry.objects.log_action(
			user_id=request.user.pk,
			content_type_id=get_content_type_for_model(object).pk,
			object_id=object.pk,
			object_repr=force_text(object),
			action_flag=ADDITION,
			change_message=message,
		)
		
	def get_context_data(self, **kwargs):
		context = super(generic.edit.CreateView, self).get_context_data(**kwargs)
		customer = self.request.GET.get('customer', '')
		advisory = self.request.GET.get('advisory', '')
		#print "before initial = %s" % (self.initial)
		if customer:
			self.initial.update({'customer': [int(customer)]})
			context['customer'] = Customer.objects.get(pk=int(customer))
		if advisory:
			self.initial.update({'advisory': int(advisory)})
			context['advisory'] = Advisory.objects.get(pk=int(advisory))
		#print "after initial = %s" % (self.initial)
		
		return context

	def form_valid(self, form):
		adv_id = self.request.GET.get('advisory', '')
		cust_id = self.request.GET.get('customer', '')
		advisory = Advisory.objects.get(pk=adv_id)
		customer = Customer.objects.get(pk=cust_id)
		form.instance.advisory = advisory
		form.instance.customer = customer
		from django.contrib.admin.utils import construct_change_message
		change_message = construct_change_message(None, None, True)
		#self.log_addition(self.request, form.instance, change_message)
		return super(DetailAddView, self).form_valid(form)
		
	def get_success_url(self):
		#self.form._set_choices(Product.objects.all().order_by('product_name').values('id', 'product_name'))
		watch = Watchlist.objects.create(user=self.request.user, content_object=self.object)
		watch.save()
		return reverse('assessment:detail', kwargs={'pk': self.object.pk})
