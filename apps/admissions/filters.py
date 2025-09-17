from django_filters import rest_framework as filters
from .models import Application

class ApplicationFilter(filters.FilterSet):
    academic_year = filters.CharFilter(field_name='intake__academic_year__year')

    class Meta:
        model = Application
        fields = ['status', 'program', 'intake', 'academic_year']