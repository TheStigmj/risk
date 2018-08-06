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
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.utils.encoding import force_text, unquote
from django.contrib.admin.models import LogEntry

from risk.models import Watchlist
import logging


class IndexView(LoginRequiredMixin, generic.ListView):
	template_name = 'watchlist/index.html'
	
	def get_queryset(self):
		return Watchlist.objects.filter(user=self.request.user).order_by('-watched__modified_date')

@login_required
def WatchlistAdd(request, content_type_id, obj_id):
	ctype = ContentType.objects.get(pk=content_type_id)
	w = Watchlist(user=request.user, content_type=ctype, object_id=obj_id)
	w.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def WatchlistRemove(request, content_type_id, obj_id):
	ctype = ContentType.objects.get(pk=content_type_id)
	w = Watchlist.objects.get(user=request.user, content_type=ctype, object_id=obj_id)
	w.delete()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
