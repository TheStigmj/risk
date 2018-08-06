#!/usr/bin/env python
###
## parse-openvuln.py (C) 2017-2018, Stig Meireles Johansen <stigmj@gmail.com>
###

from __future__ import absolute_import, unicode_literals

import sys
import StringIO
import subprocess
from datetime import tzinfo, timedelta, datetime
from dateutil.parser import parse
from risk.models import Bug, CVE, CWE, Ips_signature, Product, Advisory, Vendor, Ciscoadvisory
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
#DEBUG = False
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

	
def get_info(vuln_raw):

	data = json.loads(vuln_raw)
	now = datetime.now(utc)
	tdelta = now - timedelta(days=365)
	liste = StringIO.StringIO()
	db = StringIO.StringIO()
	debug = StringIO.StringIO()
	# get my user
	try:
		user = User.objects.get(username='cisco_import')
	except User.DoesNotExist:
		# We have to make this customer
		print "Making user cisco_import.."
		user = User.objects.create(username='cisco_import')
	# get Cisco vendor ID
	try:
		cisco = Vendor.objects.get(vendor_name='Cisco')
	except Vendor.DoesNotExist:
		# We have to make this customer
		print "Making customer Cisco.."
		cisco = Vendor.objects.create(vendor_name='Cisco')
	for vuln in sorted(data, reverse=True, key=getdate):
		print "Starting on %s" % (vuln['advisory_id'])
		products = []
		for product in vuln['product_names']:
			product = product.strip(' \t\n\r')
			#print "Check if the product \"%s\" is a part of the database" % (product)
			#Check if product is part of database
			try:
				p = Product.objects.get(product_vendor=cisco, product_name=product)
			except Product.DoesNotExist:
				print "Product \"%s\" is NOT a part of the database, adding" % (product)
				p = Product.objects.create(product_vendor=cisco, product_name=product)
				change_message = construct_change_message(None, None, True)
				log_addition(user, p, change_message)
				
			products.append(p)
		cves = []
		for cve in vuln['cves']:
			cve = cve.strip(' \t\n\r')
			#Check if cve is part of database
			try:
				p = CVE.objects.get(cve_id=cve)
			except CVE.DoesNotExist:
				print "Creating new CVE signature %s" % (cve)
				p = CVE.objects.create(cve_id=cve)
				change_message = construct_change_message(None, None, True)
				log_addition(user, p, change_message)
			cves.append(p)
		bugs = []
		for bug in vuln['bug_ids']:
			bug = bug.strip(' \t\n\r')
			#Check if bug is part of database
			try:
				p = Bug.objects.get(bug_id=bug, bug_vendor=cisco)
			except Bug.DoesNotExist:
				print "Creating new BUG id %s" % (bug)
				p = Bug.objects.create(bug_id=bug, bug_vendor=cisco)
				change_message = construct_change_message(None, None, True)
				log_addition(user, p, change_message)
			bugs.append(p)
		cwes = []
		for cwe in vuln['cwe']:
			cwe = cwe.strip(' \t\n\r')
			#Check if cwe is part of database
			try:
				p = CWE.objects.get(cwe_id=cwe)
			except CWE.DoesNotExist:
				print "Creating new CWE %s" % (cwe)
				p = CWE.objects.create(cwe_id=cwe)
				change_message = construct_change_message(None, None, True)
				log_addition(user, p, change_message)
			cwes.append(p)
		ipssigs = []
		for ipssig in vuln['ips_signatures']:
			#print "Check if the IPS signature \"%s\" is a part of the database" % (ipssig)
			if type(ipssig) is dict:
				legacy_ips_id = ipssig['legacy_ips_id'].strip(' \t\n\r')
			elif type(ipssig) is str:
				legacy_ips_id = ipssig.strip(' \t\n\r')
				ipssig = {
					"legacy_ips_id": legacy_ips_id,
					"legacy_ips_url": "",
					"release_version": "",
					"software_version": "",
				}
			else:
				legacy_ips_id = "NA"
				ipssig = {
					"legacy_ips_id": legacy_ips_id,
					"legacy_ips_url": "",
					"release_version": "",
					"software_version": "",
				}
			#Check if ipssig is part of database
			try:
				p = Ips_signature.objects.get(legacy_ips_id=legacy_ips_id)
			except Ips_signature.DoesNotExist:
				print "Creating new IPS signature %s" % (legacy_ips_id)
				p = Ips_signature.objects.create(legacy_ips_id=legacy_ips_id, legacy_ips_url=ipssig['legacy_ips_url'],
				release_version=ipssig['release_version'],software_version=ipssig['software_version'])
				change_message = construct_change_message(None, None, True)
				log_addition(user, p, change_message)
			ipssigs.append(p)
		first_published = parse(vuln['first_published'])
		last_updated = parse(vuln['last_updated'])
		# Check if this advisory exists, if not, make it
		advisory_id = vuln['advisory_id'].strip(' \t\n\r')
		try:
			advisory = Ciscoadvisory.objects.get(advisory_id=advisory_id)
		except Ciscoadvisory.DoesNotExist:
			print "Creating new Advisory ID %s" % (advisory_id)
			advisory = Ciscoadvisory.objects.create(advisory_id=advisory_id, advisory_vendor=cisco, advisory_title=vuln['advisory_title'],
			cvrf_url = vuln['cvrf_url'], cvss_base_score = vuln['cvss_base_score'], first_published = first_published,
			last_updated = last_updated, publication_url = vuln['publication_url'],
			sir = vuln['sir'], summary = vuln['summary'])
			for bug in bugs:
				advisory.bug_ids.add(bug)
			for cve in cves:
				advisory.cves.add(cve)
			for cwe in cwes:
				advisory.cwe.add(cwe)
			for ips in ipssigs:
				advisory.ips_signatures.add(ips)
			for product in products:
				advisory.product_names.add(product)
			advisory.save()
			change_message = construct_change_message(None, None, True)
			log_addition(user, advisory, change_message)
		# Check if the advisory has been updated
		if advisory.last_updated < last_updated:
			change_message = []

			print "Updating advisory ID %s" % (advisory_id)
			if vuln['advisory_title'] != advisory.advisory_title:
				advisory.advisory_title=vuln['advisory_title']
				change_message.append({
							'changed': {
								'fields': 'advisory_title',
							}
						})
			if advisory.cvrf_url != vuln['cvrf_url']:
				advisory.cvrf_url = vuln['cvrf_url']
				change_message.append({
							'changed': {
								'fields': 'cvrf_url',
							}
						})
			if advisory.cvss_base_score != vuln['cvss_base_score']:
				advisory.cvss_base_score = vuln['cvss_base_score']
				change_message.append({
							'changed': {
								'fields': 'cvss_base_score',
							}
						})
			if list(advisory.bug_ids.all()) != list(bugs):
				advisory.bug_ids.set(bugs)
				change_message.append({
							'changed': {
								'fields': 'bug_ids',
							}
						})
			if list(advisory.cves.all()) != list(cves):
				advisory.cves.set(cves)
				change_message.append({
							'changed': {
								'fields': 'cves',
							}
						})
			if list(advisory.cwe.all()) != list(cwes):
				advisory.cwe.set(cwes)
				change_message.append({
							'changed': {
								'fields': 'cwe',
							}
						})
			if advisory.first_published != first_published:
				advisory.first_published = first_published
				change_message.append({
							'changed': {
								'fields': 'first_published',
							}
						})
			if advisory.ips_signatures != ipssigs:
				advisory.ips_signatures = ipssigs
				change_message.append({
							'changed': {
								'fields': 'ips_signatures',
							}
						})
			if advisory.last_updated != last_updated:
				advisory.last_updated = last_updated
				change_message.append({
							'changed': {
								'fields': 'last_updated',
							}
						})
			if list(advisory.product_names.all()) != list(products):
				advisory.product_names.set(products)
				change_message.append({
							'changed': {
								'fields': 'product_names',
							}
						})
			if advisory.publication_url != vuln['publication_url']:
				advisory.publication_url = vuln['publication_url']
				change_message.append({
							'changed': {
								'fields': 'publication_url',
							}
						})
			if advisory.sir != vuln['sir']:
				advisory.sir = vuln['sir']
				change_message.append({
							'changed': {
								'fields': 'sir',
							}
						})
			if advisory.summary != vuln['summary']:
				advisory.summary = vuln['summary']
				change_message.append({
							'changed': {
								'fields': 'summary',
							}
						})
			advisory.save()
			log_change(user, advisory, change_message)
			#now we'll have to make all assessments of this advisory invalid
			a = Advisory.objects.get(object_id=advisory.pk, content_type=get_content_type_for_model(Ciscoadvisory))
			assessments = a.assessment_set.all()
			for assessment in assessments:
				print "Invalidating assessment %s" % (assessment)
				assessment.valid = Assessment.NO
				assessment.save()

def run(*args):
	if len(args) < 1:
			print("usage: <cvrf-file>\n")
	else:
		for arg in args:
			file = open(arg, "r")
			print get_info(file.read())
		