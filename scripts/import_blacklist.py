#!/usr/bin/env python
###
## parse-openvuln.py (C) 2017-2018, Stig Meireles Johansen <stigmj@gmail.com>
###

from __future__ import absolute_import, unicode_literals, print_function

import sys
import StringIO
import subprocess
from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse
from risk.models import Bug, CVE, CWE, Ips_signature, Product, Advisory, Customer, Vendor
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth.models import User
from django.contrib.admin.utils import construct_change_message
from django.utils.encoding import force_text, unquote
import logging

from warnings import warn

import json
from pprint import pprint

def lookahead(iterable):
	"""Pass through all values from the given iterable, augmented by the
	information if there are more values to come after the current one
	(True), or if it is the last value (False).
	"""
	# Get an iterator and pull the first value.
	it = iter(iterable)
	last = next(it)
	# Run the iterator to exhaustion (starting from the second value).
	for val in it:
		# Report the *previous* value (more to come).
		yield last, True
		last = val
	# Report the last value.
	yield last, False

CRIT_TAB = {
    'Critical': '4',
    'High': '3',
    'Medium': '2',
    'Low': '1',
    'NA': '0',
	'Informational': '50',
	'Unknown': '99',
}

def crit_tab(i):
	try:
		ret = CRIT_TAB.get(i)
	except IndexError:
		ret = '99'
	return ret

ZERO = timedelta(0)

class UTC(tzinfo):
  def utcoffset(self, dt):
    return ZERO
  def tzname(self, dt):
    return "UTC"
  def dst(self, dt):
    return ZERO

utc = UTC()


def myfunction(text):
	try:
		text = unicode(text, 'utf-8')
	except TypeError:
		return text

def getdate(a):
	return parse(a['first_published'])

	
def log_addition(user, object, message):
	"""
	Log that an object has been successfully added.

	The default implementation creates an admin LogEntry object.
	"""
	from django.contrib.admin.models import LogEntry, ADDITION
	return LogEntry.objects.log_action(
		user_id=user.pk,
		content_type_id=get_content_type_for_model(object).pk,
		object_id=object.pk,
		object_repr=force_text(object),
		action_flag=ADDITION,
		change_message=message,
	)

def log_change(user, object, message):
	"""
	Log that an object has been successfully changed.

	The default implementation creates an admin LogEntry object.
	"""
	from django.contrib.admin.models import LogEntry, CHANGE
	return LogEntry.objects.log_action(
		user_id=user.pk,
		content_type_id=get_content_type_for_model(object).pk,
		object_id=object.pk,
		object_repr=force_text(object),
		action_flag=CHANGE,
		change_message=message,
	)

def log_deletion(user, object, object_repr):
	"""
	Log that an object will be deleted. Note that this method must be
	called before the deletion.

	The default implementation creates an admin LogEntry object.
	"""
	from django.contrib.admin.models import LogEntry, DELETION
	return LogEntry.objects.log_action(
		user_id=user.pk,
		content_type_id=get_content_type_for_model(object).pk,
		object_id=object.pk,
		object_repr=object_repr,
		action_flag=DELETION,
	)
	
	
def get_info(customerid, products):

	#try:
	#	vuln_raw = subprocess.check_output("/usr/local/bin/openVulnQuery --cvrf --all", shell=True)
	#except subprocess.CalledProcessError, e:
	#	vuln_raw = e.output
	# Get customer
	customer = Customer.objects.get(id=customerid)
	try:
		cisco = Vendor.objects.get(vendor_name='Cisco')
	except Vendor.DoesNotExist:
		# We have to make this customer
		print ("Making customer Cisco..")
		cisco = Vendor.objects.create(vendor_name='Cisco')
	# Get all Products
	productsdb = Product.objects.all().filter(product_vendor=cisco)
	try:
		user = User.objects.get(username='cisco_import')
	except User.DoesNotExist:
		# We have to make this customer
		print ("Making user cisco_import..")
		user = User.objects.create(username='cisco_import')
	# Get all Bugs
	#bugsdb = Bug.objects.all()
	# Get all CVEs
	#cvesdb = CVE.objects.all()
	# Get all CWEs
	#cwesdb = CWE.objects.all()
	# Get all Ips signatures
	#ipsdb = Ips_signature.objects.all()
	# Get all advisories
	#advisorysdb = Advisory.objects.all()
	products = products.split("\n")
	print ("Found %i entries to be processed..." % (len(products)))
	#print "Found the following products in file: \"%s\"" % (products)
	for prod in productsdb:
		#print "Checking product \"%s\"" % (prod.product_name)
		#print('.', end='', flush=True)
		#test = "%s\n" % (prod.product_name)
		if prod.product_name in products and prod not in customer.blacklist.all():
			print('!', end='')
			#print "Adding product %s to blacklist" % (prod.product_name)
			customer.blacklist.add(prod)
		else:
			print('.', end='')
	customer.save()
	change_message = []
	change_message.append({
				'changed': {
					'fields': 'product_name',
				}
			})
	log_change(user, customer, change_message)

def run(*args):
	if len(args) < 1:
			print("usage: <txt-file>\n")
	else:
		for arg in args:
			file = open(arg, "r")
			
			print (get_info(1, file.read()))
		