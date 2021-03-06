# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.views import generic
from risk.models import Product, Customer, Watchlist, Advisory, Ciscoadvisory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.options import get_content_type_for_model
from bootstrap3_datetime.widgets import DateTimePicker

class ModelFormWidgetMixin(object):
	def get_form_class(self):
		return modelform_factory(self.model, fields=self.fields, widgets=self.widgets)

class IndexView(generic.ListView):
	template_name = 'advisory/index.html'
	
	def get_queryset(self):
		return Advisory.objects.order_by('-last_updated').prefetch_related('content_object')

class DetailView(generic.DetailView):
	model = Advisory
	template_name = 'advisory/detail.html'

	def get_context_data(self, **kwargs):
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		context['modelid'] = ContentType.objects.get_for_model(self.object.content_object).id
		if ContentType.objects.get_for_model(self.object.content_object) == ContentType.objects.get_for_model(Ciscoadvisory):
			self.template_name = 'advisory/ciscodetail.html'
			context['bug_ids'] = self.object.content_object.bug_ids.all()
			context['products'] = self.object.content_object.product_names.all()
		if self.request.user.is_authenticated:
			try:
				context['watchlist'] = Watchlist.objects.get(user=self.request.user, content_type=context['modelid'], object_id=self.object.id)
			except Watchlist.DoesNotExist:
				context['watchlist'] = None
		return context

class DetailUpdateView(LoginRequiredMixin, ModelFormWidgetMixin, generic.edit.UpdateView):
	model = Advisory
	template_name = 'advisory/edit.html'
	#form_class = AssessmentEditForm
	fields = '__all__'
	widgets = {
		'last_updated': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
			"calendarWeeks": True,
			"showTodayButton": True,
			}),
		'first_published': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
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

	def get_object(self):
		
		try:
			up = Userprofile.objects.get(user=self.request.user.id, wlnumber=self.kwargs['number'])
		except Userprofile.DoesNotExist:
			up = None
		return up
		
	def get_context_data(self, **kwargs):
		context = super(generic.edit.UpdateView, self).get_context_data(**kwargs)
		if ContentType.objects.get_for_model(self.object.content_object) == ContentType.objects.get_for_model(Ciscoadvisory):
			self.model
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
		return reverse('advisory:detail', kwargs={'pk': self.object.pk})
		
class DetailUpdateView(LoginRequiredMixin, generic.edit.UpdateView):
	model = Advisory
	template_name = 'advisory/detail.html'

	def get_context_data(self, **kwargs):
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		context['modelid'] = ContentType.objects.get_for_model(self.object.content_object).id
		if ContentType.objects.get_for_model(self.object.content_object) == ContentType.objects.get_for_model(Ciscoadvisory):
			self.template_name = 'advisory/ciscodetail.html'
			context['bug_ids'] = self.object.content_object.bug_ids.all()
			context['products'] = self.object.content_object.product_names.all()
		if self.request.user.is_authenticated:
			try:
				context['watchlist'] = Watchlist.objects.get(user=self.request.user, content_type=context['modelid'], object_id=self.object.id)
			except Watchlist.DoesNotExist:
				context['watchlist'] = None
		return context
		
class DetailAddView(LoginRequiredMixin, generic.edit.CreateView):
	model = Advisory
	template_name = 'advisory/detail.html'

	def get_context_data(self, **kwargs):
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		context['modelid'] = ContentType.objects.get_for_model(self.object.content_object).id
		if ContentType.objects.get_for_model(self.object.content_object) == ContentType.objects.get_for_model(Ciscoadvisory):
			self.template_name = 'advisory/ciscodetail.html'
			context['bug_ids'] = self.object.content_object.bug_ids.all()
			context['products'] = self.object.content_object.product_names.all()
		if self.request.user.is_authenticated:
			try:
				context['watchlist'] = Watchlist.objects.get(user=self.request.user, content_type=context['modelid'], object_id=self.object.id)
			except Watchlist.DoesNotExist:
				context['watchlist'] = None
		return context