from django.contrib import admin
from .models import (
    Pollutant, Country, City, MeasurementStation,
    AirQualityData, HealthImpact, DataSource, Evaluation
)


class ManuallyEditedMixin:
    """Mixin qui marque automatiquement un enregistrement comme édité manuellement
    lors d'une sauvegarde admin, SAUF si l'admin a explicitement décoché le champ."""

    def save_model(self, request, obj, form, change):
        # Si l'admin n'a pas explicitement décoché manually_edited, on le force à True
        if 'manually_edited' not in form.changed_data or form.cleaned_data.get('manually_edited'):
            obj.manually_edited = True
        super().save_model(request, obj, form, change)


@admin.register(Pollutant)
class PollutantAdmin(ManuallyEditedMixin, admin.ModelAdmin):
    list_display = ('symbol', 'name', 'limit_oms', 'unit', 'manually_edited')
    list_filter = ('manually_edited',)
    search_fields = ('name', 'symbol')


@admin.register(Country)
class CountryAdmin(ManuallyEditedMixin, admin.ModelAdmin):
    list_display = ('code', 'name', 'region', 'population', 'manually_edited')
    list_filter = ('manually_edited',)
    search_fields = ('name', 'code')


@admin.register(City)
class CityAdmin(ManuallyEditedMixin, admin.ModelAdmin):
    list_display = ('name', 'country', 'population', 'manually_edited')
    list_filter = ('country', 'manually_edited')
    search_fields = ('name',)


@admin.register(MeasurementStation)
class MeasurementStationAdmin(ManuallyEditedMixin, admin.ModelAdmin):
    list_display = ('name', 'city', 'is_active', 'altitude', 'manually_edited')
    list_filter = ('is_active', 'city__country', 'manually_edited')
    search_fields = ('name', 'city__name')


@admin.register(AirQualityData)
class AirQualityDataAdmin(ManuallyEditedMixin, admin.ModelAdmin):
    list_display = ('pollutant', 'station', 'value', 'measurement_date', 'is_valid', 'manually_edited')
    list_filter = ('pollutant', 'is_valid', 'manually_edited', 'measurement_date')
    search_fields = ('station__name', 'pollutant__symbol')
    date_hierarchy = 'measurement_date'


@admin.register(HealthImpact)
class HealthImpactAdmin(ManuallyEditedMixin, admin.ModelAdmin):
    list_display = ('disease', 'pollutant', 'annual_deaths_europe', 'manually_edited')
    list_filter = ('pollutant', 'manually_edited')
    search_fields = ('disease',)


@admin.register(DataSource)
class DataSourceAdmin(ManuallyEditedMixin, admin.ModelAdmin):
    list_display = ('name', 'source_type', 'last_update', 'manually_edited')
    list_filter = ('source_type', 'manually_edited')
    search_fields = ('name', 'url')


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved')
    search_fields = ('author_name', 'comment')
    actions = ['approve', 'reject']

    @admin.action(description='Approuver les évaluations sélectionnées')
    def approve(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Masquer les évaluations sélectionnées')
    def reject(self, request, queryset):
        queryset.update(is_approved=False)
