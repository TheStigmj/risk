# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.http import HttpResponse

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, IntegerField
from django import forms

from risk.models import Customer,Product
from customer.forms import CustomerEditForm, CustomerEditForm2
import logging


class IndexView(LoginRequiredMixin, generic.ListView):
	template_name = 'customer/index.html'
	
	def get_queryset(self):
		"""Return the last five published questions."""
		return Customer.objects.order_by('customer_name')

class CustomerDetail(LoginRequiredMixin, generic.DetailView):
	model = Customer
	template_name = 'customer/detail.html'

	def get_context_data(self, **kwargs):
		#l = logging.getLogger('django.db.backends')
		#l.setLevel(logging.DEBUG)
		#l.addHandler(logging.StreamHandler())
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		context['blacklist'] = self.object.blacklist.all().order_by('product_name')
		#print "woot"
		#context['products'] = Product.objects.annotate(is_blacklisted=Case(When(id__in=blacklist, then=1), default=0, output_field=IntegerField())).order_by('product_name')
		#context['products'] = Product.objects.filter(id__in=blacklist)
		#print "woot %s" % (context['products'])
		#context['products'] = Product.objects.all().prefetch_related('customer__blacklist')
		#context['products'] = Product.objects.all()
		#context['cves'] = self.object.cves.all()
		#context['cwe'] = self.object.cwe.all()
		#context['ips_signatures'] = self.object.ips_signatures.all()
		#context['products'] = self.object.product_names.all()
		#context['form'] = CustomerEditForm(customer=self.object.pk)
		#context['form'] = CustomerEditForm2(initial={'blacklist': [c.pk for c in blacklist]})
		return context
		
		
class CustomerDetailView(LoginRequiredMixin, generic.DetailView):
	model = Customer
	template_name = 'customer/edit.html'

	def get_context_data(self, **kwargs):
		#l = logging.getLogger('django.db.backends')
		#l.setLevel(logging.DEBUG)
		#l.addHandler(logging.StreamHandler())
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		blacklist = self.object.blacklist.all().order_by('product_name')
		#print "woot"
		#context['products'] = Product.objects.annotate(is_blacklisted=Case(When(id__in=blacklist, then=1), default=0, output_field=IntegerField())).order_by('product_name')
		#context['products'] = Product.objects.filter(id__in=blacklist)
		#print "woot %s" % (context['products'])
		#context['products'] = Product.objects.all().prefetch_related('customer__blacklist')
		#context['products'] = Product.objects.all()
		#context['cves'] = self.object.cves.all()
		#context['cwe'] = self.object.cwe.all()
		#context['ips_signatures'] = self.object.ips_signatures.all()
		#context['products'] = self.object.product_names.all()
		context['form'] = CustomerEditForm(customer=self.object.pk)
		#context['form'] = CustomerEditForm2(initial={'blacklist': [c.pk for c in blacklist]})
		return context
	
class CustomerEditView(LoginRequiredMixin, generic.detail.SingleObjectMixin, generic.FormView):
	template_name = 'customer/edit.html'
	form_class = CustomerEditForm
	model = Customer

	#def __init__(self, *args, **kwargs):
	#	super(CustomerEditView, self).__init__(*args, **kwargs)
	#	self.form_class = CustomerEditForm(customer=self.object.pk)
		
	def post(self, request, *args, **kwargs):
		#if not request.user.is_authenticated:
		#    return HttpResponseForbidden()
		self.object = self.get_object()
		#self.form_class = CustomerEditForm(customer=self.object.pk)
		#self.form._set_choices(Product.objects.all().order_by('product_name').values('id', 'product_name'))
		#self.form_class = CustomerEditForm(customer=self.object.pk)
		return super(CustomerEditView, self).post(request, *args, **kwargs)
	
	def form_valid(self, form):
		#print form.cleaned_data['blacklist']
		#l = logging.getLogger('django.db.backends')
		#l.setLevel(logging.DEBUG)
		#l.addHandler(logging.StreamHandler())
		self.object.blacklist = form.cleaned_data['blacklist']
		self.object.save()
		return super(CustomerEditView, self).form_valid(form)
		
	def get_success_url(self):
		#self.form._set_choices(Product.objects.all().order_by('product_name').values('id', 'product_name'))
		return reverse('customer:detail', kwargs={'pk': self.object.pk})
		
class CustomerEdit(View):
	
	def get(self, request, *args, **kwargs):
		view = CustomerDetailView.as_view()
		return view(request, *args, **kwargs)
	
	def post(self, request, *args, **kwargs):
		view = CustomerEditView.as_view()
		return view(request, *args, **kwargs)