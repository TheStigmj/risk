# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Bug, CVE, CWE, Ips_signature, Product, Advisory, Customer, Assessment, Riskmatrix, Vendor, Watchlist, Userprofile, Ciscoadvisory
from django.contrib.admin.models import LogEntry

admin.site.register(Ciscoadvisory)
admin.site.register(Advisory)
admin.site.register(Bug)
admin.site.register(CVE)
admin.site.register(CWE)
admin.site.register(Ips_signature)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Assessment)
admin.site.register(Riskmatrix)
admin.site.register(Vendor)
admin.site.register(Watchlist)
admin.site.register(Userprofile)
admin.site.register(LogEntry)
