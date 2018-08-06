import django_tables2 as tables
from django_tables2.utils import A
from risk.models import Advisory, Product, Customer, Assessment

class RiskTable(tables.Table):
	#advisory_id = tables.LinkColumn('advisory-detail', args=[A('pk')])
    
	class Meta:
		model = Advisory
		fields = ('last_updated', 'advisory_id',
				'sir', 'summary')
		attrs = {"class": "table-striped table-bordered"}
		empty_text = "There are no advisories matching the search criteria..."