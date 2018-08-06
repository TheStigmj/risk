# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.admin.options import get_content_type_for_model

class BaseModel(models.Model):
	created_date = models.DateTimeField(auto_now_add=True, editable=False)
	modified_date = models.DateTimeField(auto_now=True)
	watchlist = GenericRelation('Watchlist', related_query_name='watched')
	
	class Meta:
		abstract = True

class Bug(BaseModel):
	bug_id = models.CharField(max_length=100)
	bug_vendor = models.ForeignKey(
        'Vendor', null=True, default=1,
	)
	
	def __str__(self):
		return self.bug_id
	
class CVE(BaseModel):
	cve_id = models.CharField(max_length=100)
	
	def __str__(self):
		return self.cve_id

	
class CWE(BaseModel):
	cwe_id = models.CharField(max_length=100)
	
	def __str__(self):
		return self.cwe_id


class Ips_signature(BaseModel):
#            {
#                "legacy_ips_id": "cisco-sa-20180328-smi2", 
#                "legacy_ips_url": "https://tools.cisco.com/security/center/viewIpsSignature.x?signatureId=8190&signatureSubId=0&softwareVersion=6.0&releaseVersion=S1014", 
#                "release_version": "S1014", 
#                "software_version": "6.0"
#            }, 
	legacy_ips_id = models.CharField(max_length=100)
	legacy_ips_url = models.CharField(max_length=2048)
	release_version = models.CharField(max_length=100)
	software_version = models.CharField(max_length=100)
	
	def __str__(self):
		return self.legacy_ips_id

class Vendor(BaseModel):
	vendor_name = models.CharField(max_length=255)
	
	def __str__(self):
		return self.vendor_name
		
class Product(BaseModel):
	product_name = models.CharField(max_length=255)
	product_vendor = models.ForeignKey(
        'Vendor', null=True, default=1,
	)
	
	def __str__(self):
		return self.product_name
	

class Riskmatrix(BaseModel):
	CRITICAL = 40
	HIGH = 30
	MEDIUM = 20
	LOW = 10
	NONE = 5
	INFORMATIONAL = 0
	UNKNOWN = -10
	ASSESSMENT_CHOICES = (
		(CRITICAL, 'Critical'),
		(HIGH, 'High'),
		(MEDIUM, 'Medium'),
		(LOW, 'Low'),
		(INFORMATIONAL, 'Informational'),
		(NONE, 'None'),
		(UNKNOWN, 'Unknown'),
	)
	name = models.CharField(max_length=255)
	matrix = models.TextField(max_length=65535)
	colors = models.TextField(max_length=65535, blank=True)
	def __str__(self):
		return self.name
		
class Customer(BaseModel):
	customer_name = models.CharField(max_length=255)
	blacklist = models.ManyToManyField(Product, blank=True)
	riskmatrix = models.ForeignKey(
        'Riskmatrix',
	)

	def __str__(self):
		return self.customer_name

class Assessment(BaseModel):
	YES = 'Y'
	NO = 'N'
	VALID_CHOICES = (
		(YES, 'Yes'),
		(NO, 'No'),
	)
	advisory = models.ForeignKey(
        'Advisory',
        on_delete=models.CASCADE,
	)
	customer = models.ForeignKey(
		'Customer', 
		on_delete=models.CASCADE,
	)
	probability = models.IntegerField(
		choices=Riskmatrix.ASSESSMENT_CHOICES,
		default=Riskmatrix.UNKNOWN,
	)
	consequence = models.IntegerField(
		choices=Riskmatrix.ASSESSMENT_CHOICES,
		default=Riskmatrix.UNKNOWN,
	)
	risk_description = models.TextField(max_length=65535, blank=True, null=True)
	probability_description = models.TextField(max_length=65535, blank=True, null=True)
	consequence_description = models.TextField(max_length=65535, blank=True, null=True)
	valid = models.CharField(
		choices=VALID_CHOICES,
		default=YES,
		max_length=1,
	)
	probability_after_action = models.IntegerField(
		choices=Riskmatrix.ASSESSMENT_CHOICES,
		default=Riskmatrix.UNKNOWN,
		blank=True,
		null=True,
	)
	consequence_after_action = models.IntegerField(
		choices=Riskmatrix.ASSESSMENT_CHOICES,
		default=Riskmatrix.UNKNOWN,
		blank=True,
		null=True,
	)
	action_description = models.TextField(max_length=65535, blank=True, null=True)
	mitigated_date = models.DateTimeField('date mitigated', blank=True, null=True)
	
	def __str__(self):
		return "%s - %s" % (self.advisory.content_object.advisory_id, self.customer.customer_name)
		
class Ciscoadvisory(BaseModel):
	advisory_id = models.CharField(max_length=100)
	advisory_vendor = models.ForeignKey(
        'Vendor', null=True, default=1,
	)
	advisory_title = models.CharField(max_length=255)
	bug_ids = models.ManyToManyField(Bug)
	cves = models.ManyToManyField(CVE)
	cvrf_url = models.CharField(max_length=2048)
	cvss_base_score = models.CharField(max_length=100)
	cwe = models.ManyToManyField(CWE)
	first_published = models.DateTimeField('date published')
	ips_signatures = models.ManyToManyField(Ips_signature)
	last_updated = models.DateTimeField('date updated')
	product_names = models.ManyToManyField(Product)
	publication_url = models.CharField(max_length=2048)
	sir = models.CharField(max_length=100)
	summary = models.TextField(max_length=65535)
	advisory = GenericRelation('Advisory', related_query_name='adv')

	def __str__(self):
		return self.advisory_id

class Advisory(models.Model):
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	last_updated = models.DateTimeField('date updated')
	
	def __str__(self):
		return "%s - %s" % (self.content_type, self.content_object)		

@receiver(post_save, sender=Ciscoadvisory)
def create_advisory(sender, instance, created, **kwargs):
	print "post_save signal"
	if created:
		print "post_save signal says it was CREATED"
		Advisory.objects.create(content_object=instance, last_updated=instance.last_updated)
	else:
		advisory = Advisory.objects.get(object_id=instance.pk, content_type=get_content_type_for_model(Ciscoadvisory))
		advisory.last_updated = instance.last_updated
		advisory.save()
		
class Watchlist(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
	)
	notificationtimestamp = models.DateTimeField(blank=True,null=True)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	
	def __str__(self):
		return "%s - %s - %s" % (self.user.username, self.content_type, self.content_object)

class Userprofile(models.Model):
	NONE = 0
	EMAIL = 1
	SMS = 10
	VALID_CHOICES = (
		(NONE, 'none'),
		(EMAIL, 'email'),
		(SMS, 'sms'),
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	wlnumber = models.PositiveIntegerField(default=1)
	wlnotify = models.IntegerField(
		choices=VALID_CHOICES,
		default=NONE,
	)
	wltext = models.CharField(max_length=130, blank=True)
	wlemail = models.TextField(max_length=65535, blank=True)
	wlsms = models.TextField(max_length=65535, blank=True)
	
	def __str__(self):
		return "%s - #%i" % (self.user.username, self.wlnumber)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Userprofile.objects.create(user=instance)

#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#	instance.userprofile.save()
