# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.http import HttpResponse

from django.urls import reverse
from django.views import generic, View
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.utils.encoding import force_text, unquote
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import get_content_type_for_model

from risk.models import Watchlist, Customer,Product, Userprofile
from userprofile.forms import UserprofileEditForm
import logging


class UserprofileIndex(LoginRequiredMixin, generic.ListView):
	template_name = 'userprofile/index.html'
	
	def get_queryset(self):
		return Userprofile.objects.filter(user=self.request.user).order_by('wlnumber')
#	def get_context_data(self, **kwargs):
#		context = super(generic.ListView, self).get_context_data(**kwargs)
#		last_action = LogEntry.objects.filter(
#			object_id=unquote(self.object.pk),
#			content_type=self.object.content_type
#		).select_related().latest('action_time')
#		context['last_action'] = last_action
#		context['products'] = self.object.product.all().order_by('product_name')
#		return context
	
class UserprofileDetail(LoginRequiredMixin, generic.DetailView):
	model = Userprofile
	template_name = 'userprofile/detail.html'

	def get_object(self):
		
		try:
			up = Userprofile.objects.get(user=self.request.user.id, wlnumber=self.kwargs['number'])
		except Userprofile.DoesNotExist:
			up = None
		return up

	def get_context_data(self, **kwargs):
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		context['user'] = self.request.user
		return context

		
class UserprofileUpdateView(LoginRequiredMixin, generic.edit.UpdateView):
	model = Userprofile
	template_name = 'userprofile/edit.html'
	#form_class = AssessmentEditForm
	fields = ['wlnotify','wlemail','wlsms']

	def get_object(self):
		try:
			up = Userprofile.objects.get(user=self.request.user.id, wlnumber=self.kwargs['number'])
		except Userprofile.DoesNotExist:
			up = None
		return up
	
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
		context = super(UserprofileUpdateView, self).get_context_data(**kwargs)
		
		return context
		
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(UserprofileUpdateView, self).post(request, *args, **kwargs)
	
	def form_valid(self, form):
		from django.contrib.admin.utils import construct_change_message
		change_message = construct_change_message(form, None, None)
		self.log_change(self.request, self.object, change_message)
		return super(UserprofileUpdateView, self).form_valid(form)
		
	def get_success_url(self):
		#self.form._set_choices(Product.objects.all().order_by('product_name').values('id', 'product_name'))
		return reverse('userprofile:detail', kwargs={'number': self.object.wlnumber})
		
class UserprofileAddView(LoginRequiredMixin, generic.edit.CreateView):
	model = Userprofile
	template_name = 'assessment/edit.html'
	#form_class = AssessmentAddForm
	fields = ['wlnotify','wlemail','wlsms']
	#fields = ['advisory','customer','valid','consequence','consequence_description','probability','probability_description','risk_description','action']
	initial = {}
		
	def get_context_data(self, **kwargs):
		context = super(UserprofileAddView, self).get_context_data(**kwargs)
		customer = self.request.GET.get('customer', '')
		advisory = self.request.GET.get('advisory', '')
		#print "before initial = %s" % (self.initial)
		if customer:
			self.initial.update({'customer': [int(customer)]})
		if advisory:
			self.initial.update({'advisory': int(advisory)})
		#print "after initial = %s" % (self.initial)
		
		return context
		
	def get_success_url(self):
		#self.form._set_choices(Product.objects.all().order_by('product_name').values('id', 'product_name'))
		return reverse('userprofile:detail', kwargs={'number': self.object.wlnumber})		
		
class UserprofileDetailView(LoginRequiredMixin, generic.UpdateView):
	model = Userprofile
	template_name = 'userprofile/edit.html'
	#form_class = AssessmentEditForm
	fields = ['wlnotify', 'wlemail', 'wlsms']

	def get_object(self):
		try:
			up = Userprofile.objects.get(user=self.request.user.id, wlnumber=self.kwargs['number'])
		except Userprofile.DoesNotExist:
			up = None
		return up

	def get_context_data(self, **kwargs):
		#l = logging.getLogger('django.db.backends')
		#l.setLevel(logging.DEBUG)
		#l.addHandler(logging.StreamHandler())
		context = super(UserprofileDetailView, self).get_context_data(**kwargs)
		#blacklist = self.object.blacklist.all().order_by('product_name')
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
		#context['form'] = ProfileEditForm()
		#context['form'] = CustomerEditForm2(initial={'blacklist': [c.pk for c in blacklist]})
		return context

	def get_context_data(self, **kwargs):
		context = super(UserprofileDetailView, self).get_context_data(**kwargs)
		
		return context
		
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(UserprofileDetailView, self).post(request, *args, **kwargs)
	
	def form_valid(self, form):
		from django.contrib.admin.utils import construct_change_message
		change_message = construct_change_message(form, None, None)
		self.log_change(self.request, self.object, change_message)
		return super(UserprofileDetailView, self).form_valid(form)
		
	def get_success_url(self):
		#self.form._set_choices(Product.objects.all().order_by('product_name').values('id', 'product_name'))
		return reverse('userprofile:detail', kwargs={'number': self.object.wlnumber})

		
		
class UserprofileEditView(LoginRequiredMixin, generic.detail.SingleObjectMixin, generic.FormView):
	template_name = 'userprofile/edit.html'
	#form_class = CustomerEditForm
	model = Userprofile

	def get_object(self):
		try:
			up = Userprofile.objects.get(user=self.request.user.id, wlnumber=self.kwargs['number'])
		except Userprofile.DoesNotExist:
			up = None
		return up
		
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super(UserprofileEditView, self).post(request, *args, **kwargs)
	
#	def form_valid(self, form):
#		self.object.blacklist = form.cleaned_data['blacklist']
#		self.object.save()
#		return super(UserprofileEditView, self).form_valid(form)
		
	def get_success_url(self):
		return reverse('userprofile:detail', kwargs={'number': self.object.wlnumber})
		
class UserprofileEdit(LoginRequiredMixin,View):
	
	def get(self, request, *args, **kwargs):
		view = UserprofileDetailView.as_view()
		return view(request, *args, **kwargs)
	
	def post(self, request, *args, **kwargs):
		view = UserprofileEditView.as_view()
		return view(request, *args, **kwargs)