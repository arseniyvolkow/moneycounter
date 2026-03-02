import django_filters
from finance.models import Transaction

class TransactionFilter(django_filters.FilterSet):
    """
    FilterSet for the Transaction model.
    Allows filtering transactions by category and a date range.
    """
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    category = django_filters.NumberFilter(field_name='category')

    class Meta:
        model = Transaction
        fields = ['category', 'start_date', 'end_date']