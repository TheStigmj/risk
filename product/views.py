# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.views import generic
from risk.models import Product, Customer, Watchlist
from django.contrib.contenttypes.models import ContentType

class IndexView(generic.ListView):
	template_name = 'product/index.html'
	
	def get_queryset(self):
		return Product.objects.order_by('product_vendor__vendor_name', 'product_name')

class DetailView(generic.DetailView):
	model = Product
	template_name = 'product/detail.html'

	def get_context_data(self, **kwargs):
		context = super(generic.DetailView, self).get_context_data(**kwargs)
		context['advisories'] = self.object.advisory_set.all()
		context['modelid'] = ContentType.objects.get_for_model(Product).id
		if self.request.user.is_authenticated:
			try:
				context['watchlist'] = Watchlist.objects.get(user=self.request.user, content_type=context['modelid'], object_id=self.object.id)
			except Watchlist.DoesNotExist:
				context['watchlist'] = None
		customers = Customer.objects.all()
		customers = customers.exclude(id__in=self.object.customer_set.all())
		context['customers'] = customers
		return context