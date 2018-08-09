# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.http import HttpResponse

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.db.models import Subquery
from django_tables2 import RequestConfig
from risk.tables import RiskTable
from risk.forms import CustomerSelectForm

from risk.models import Advisory, Product, Customer, Assessment
import logging, json
import inspect
from datetime import date

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
	
class IndexView(generic.ListView):
	template_name = 'risk/index.html'
	_customer = None

	def get_queryset(self):
		#l = logging.getLogger('django.db.backends')
		#l.setLevel(logging.DEBUG)
		#l.addHandler(logging.StreamHandler())
		queryset = None
		#First, let's get all advisories, reverse ordered by last_updated
		queryset = Advisory.objects.order_by('-adv__last_updated')
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
				blacklist = self._customer.blacklist.all()
				#blacklist = Customer.objects.get(pk=cust).blacklist.all()
				# Build a whitelist of products excluding the blacklist from the customer
				whitelist = Product.objects.all().exclude(id__in=blacklist)
				# Need to filter out mitigated advisories
				filter_date = date.today()
				#mitigated = Assessment.objects.all().filter(customer=self._customer)
				#mitigated = Assessment.objects.all().filter(customer=self._customer).filter(mitigated_date<=filter_date)
				assessment_filter = Assessment.objects.all().filter(customer=self._customer)
				assessment_filter = assessment_filter.filter(mitigated_date__lte=filter_date)
				# And filter the queryset with the new whitelist
				#queryset = queryset.filter(adv__product_names__in=whitelist).exclude(adv__assessment__in=assessment_filter).distinct()
				queryset = queryset.filter(adv__product_names__in=whitelist).distinct().prefetch_related('content_object')

		return queryset
		
	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data(**kwargs)

		context['table_filter_date'] = None
		context['table_filter_sir'] = None
		context['table_filter_consequence'] = None
		context['table_filter_probability'] = None
		context['table_filter_risk'] = None
		# Are we looking at a specific customer?
		if self._customer:
			# Yes, so we'll add some contexts for use in the template
			test = self._customer.riskmatrix.matrix
			context['riskmatrix'] = json.loads(self._customer.riskmatrix.matrix)
			context['riskcolors'] = json.loads(self._customer.riskmatrix.colors)
			context['customer'] = self._customer
			context['customer_id'] = self._customer.id
			# Get all assessments made for this customer
			context['assessment_list'] = Assessment.objects.all().filter(customer=self._customer).prefetch_related('advisory')
			context['customer_selectform'] = CustomerSelectForm(initial={'customer': self._customer.id})
		else:
			context['customer_selectform'] = CustomerSelectForm()
			context['customer'] = None
			context['customer_id'] = None
		return context

	def get_form_kwargs(self):
		print "entering get_form_kwargs"
		kwargs = super().get_form_kwargs()
		print "in get_form_kwargs and self.request = %s" % (introspect(self.request))
		kwargs.update({'request': self.request})
		return kwargs

		
class DetailView(generic.DetailView):
	model = Advisory
	template_name = 'risk/detail.html'

	def get_context_data(self, **kwargs):
		context = super(generic.DetailView, self).get_context_data(**kwargs)

		context['bug_ids'] = self.object.bug_ids.all()
		context['cves'] = self.object.cves.all()
		context['cwe'] = self.object.cwe.all()
		context['ips_signatures'] = self.object.ips_signatures.all()
		context['products'] = self.object.product_names.all()
		return context