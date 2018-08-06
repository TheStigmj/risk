# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.views import generic

from risk.models import Advisory, Product, Customer, Assessment
from django.contrib.auth.models import User

import logging
	
class HomePageView(generic.TemplateView):
	template_name = 'risksite/index.html'
	_customer = None
		
	def get_context_data(self, **kwargs):
		context = super(generic.TemplateView, self).get_context_data(**kwargs)
		context['num_customers'] = Customer.objects.all().count()
		context['num_advisories'] = Advisory.objects.all().count()
		context['num_assessments'] = Assessment.objects.all().count()
		context['num_products'] = Product.objects.all().count()
		context['num_users'] = User.objects.all().count()
		return context
		