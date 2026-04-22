from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Avg, Max, Min, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import (
    Pollutant, Country, City, MeasurementStation,
    AirQualityData, HealthImpact, DataSource, Evaluation
)
from .forms import CityForm, AirQualityDataForm, PollutantForm, EvaluationForm
from django.utils import timezone
from datetime import timedelta


def is_admin(user):
    return user.is_active and user.is_staff


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('airquality:index')
        return render(request, 'airquality/login.html')

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'airquality:index')
            return redirect(next_url)
        messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        return render(request, 'airquality/login.html')


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('airquality:index')


# ---------------------------------------------------------------------------
# Public views
# ---------------------------------------------------------------------------

class IndexView(View):
    """Page d'accueil avec statistiques clés"""
    def get(self, request):
        context = {
            'total_stations': MeasurementStation.objects.filter(is_active=True).count(),
            'total_countries': Country.objects.count(),
            'total_cities': City.objects.count(),
            'pollutants': Pollutant.objects.all(),
            'latest_data': AirQualityData.objects.select_related(
                'station', 'pollutant'
            ).order_by('-measurement_date')[:10],
            'stats': {
                'premature_deaths': 400000,
                'active_stations': MeasurementStation.objects.filter(is_active=True).count(),
                'monitored_countries': Country.objects.count(),
                'pm25_reduction': 30,
            }
        }
        return render(request, 'airquality/index.html', context)


class DataView(View):
    """Page données et statistiques"""
    def get(self, request):
        pollutants = Pollutant.objects.all()
        pollutant_stats = []
        for pollutant in pollutants:
            measurements = AirQualityData.objects.filter(
                pollutant=pollutant,
                is_valid=True,
                measurement_date__gte=timezone.now() - timedelta(days=365)
            )
            if measurements.exists():
                stats = measurements.aggregate(
                    avg_value=Avg('value'),
                    max_value=Max('value'),
                    min_value=Min('value'),
                    total_count=Count('id')
                )
                pollutant_stats.append({
                    'pollutant': pollutant,
                    'avg': stats['avg_value'],
                    'max': stats['max_value'],
                    'min': stats['min_value'],
                    'count': stats['total_count'],
                })
        context = {
            'pollutants': pollutants,
            'pollutant_stats': pollutant_stats,
            'cities': City.objects.all()[:10],
        }
        return render(request, 'airquality/data.html', context)


class MapView(View):
    """Page carte interactive"""
    def get(self, request):
        stations = MeasurementStation.objects.filter(is_active=True).select_related(
            'city', 'city__country'
        )
        context = {
            'stations': stations,
            'cities': City.objects.all(),
        }
        return render(request, 'airquality/map.html', context)


class CityDetailView(View):
    """Détails d'une ville"""
    def get(self, request, city_id):
        city = get_object_or_404(City, pk=city_id)
        stations = city.stations.filter(is_active=True)
        latest_measurements = AirQualityData.objects.filter(
            station__city=city,
            is_valid=True,
            measurement_date__gte=timezone.now() - timedelta(days=7)
        ).select_related('pollutant', 'station').order_by('-measurement_date')
        context = {
            'city': city,
            'stations': stations,
            'latest_measurements': latest_measurements,
        }
        return render(request, 'airquality/city_detail.html', context)


class ImpactsView(View):
    """Page impacts sanitaires"""
    def get(self, request):
        health_impacts = HealthImpact.objects.select_related('pollutant').all()
        context = {
            'health_impacts': health_impacts,
            'total_deaths': sum(h.annual_deaths_europe for h in health_impacts)
        }
        return render(request, 'airquality/impacts.html', context)


class SourcesView(View):
    """Page sources de données"""
    def get(self, request):
        sources = DataSource.objects.all()
        context = {'sources': sources}
        return render(request, 'airquality/sources.html', context)


# ---------------------------------------------------------------------------
# Evaluations (public)
# ---------------------------------------------------------------------------

class EvaluationsView(View):
    """Page évaluations utilisateurs"""
    def get(self, request):
        evaluations = Evaluation.objects.filter(is_approved=True)
        avg = evaluations.aggregate(avg=Avg('rating'))['avg'] or 0
        form = EvaluationForm()
        context = {
            'evaluations': evaluations,
            'avg_rating': round(avg, 1),
            'total': evaluations.count(),
            'form': form,
        }
        return render(request, 'airquality/evaluations.html', context)

    def post(self, request):
        form = EvaluationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Merci pour votre évaluation !')
            return redirect('airquality:evaluations')
        evaluations = Evaluation.objects.filter(is_approved=True)
        avg = evaluations.aggregate(avg=Avg('rating'))['avg'] or 0
        context = {
            'evaluations': evaluations,
            'avg_rating': round(avg, 1),
            'total': evaluations.count(),
            'form': form,
        }
        return render(request, 'airquality/evaluations.html', context)


# ---------------------------------------------------------------------------
# Admin dashboard & CRUD (staff only)
# ---------------------------------------------------------------------------

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        context = {
            'cities_count': City.objects.count(),
            'measurements_count': AirQualityData.objects.count(),
            'pollutants_count': Pollutant.objects.count(),
            'evaluations_count': Evaluation.objects.count(),
            'cities': City.objects.select_related('country').all(),
            'recent_measurements': AirQualityData.objects.select_related(
                'station', 'pollutant'
            ).order_by('-measurement_date')[:20],
            'pollutants': Pollutant.objects.all(),
            'evaluations': Evaluation.objects.all(),
        }
        return render(request, 'airquality/admin_dashboard.html', context)


# --- City CRUD ---

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class CityCreateView(View):
    def get(self, request):
        form = CityForm()
        return render(request, 'airquality/city_form.html', {'form': form, 'action': 'Ajouter'})

    def post(self, request):
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ville ajoutée avec succès.')
            return redirect('airquality:admin_dashboard')
        return render(request, 'airquality/city_form.html', {'form': form, 'action': 'Ajouter'})


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class CityUpdateView(View):
    def get(self, request, city_id):
        city = get_object_or_404(City, pk=city_id)
        form = CityForm(instance=city)
        return render(request, 'airquality/city_form.html', {'form': form, 'action': 'Modifier', 'object': city})

    def post(self, request, city_id):
        city = get_object_or_404(City, pk=city_id)
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ville modifiée avec succès.')
            return redirect('airquality:admin_dashboard')
        return render(request, 'airquality/city_form.html', {'form': form, 'action': 'Modifier', 'object': city})


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class CityDeleteView(View):
    def get(self, request, city_id):
        city = get_object_or_404(City, pk=city_id)
        return render(request, 'airquality/confirm_delete.html', {'object': city, 'type': 'ville'})

    def post(self, request, city_id):
        city = get_object_or_404(City, pk=city_id)
        city.delete()
        messages.success(request, 'Ville supprimée.')
        return redirect('airquality:admin_dashboard')


# --- AirQualityData CRUD ---

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class MeasurementCreateView(View):
    def get(self, request):
        form = AirQualityDataForm()
        return render(request, 'airquality/measurement_form.html', {'form': form, 'action': 'Ajouter'})

    def post(self, request):
        form = AirQualityDataForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesure ajoutée avec succès.')
            return redirect('airquality:admin_dashboard')
        return render(request, 'airquality/measurement_form.html', {'form': form, 'action': 'Ajouter'})


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class MeasurementUpdateView(View):
    def get(self, request, pk):
        measurement = get_object_or_404(AirQualityData, pk=pk)
        form = AirQualityDataForm(instance=measurement)
        return render(request, 'airquality/measurement_form.html', {'form': form, 'action': 'Modifier', 'object': measurement})

    def post(self, request, pk):
        measurement = get_object_or_404(AirQualityData, pk=pk)
        form = AirQualityDataForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesure modifiée avec succès.')
            return redirect('airquality:admin_dashboard')
        return render(request, 'airquality/measurement_form.html', {'form': form, 'action': 'Modifier', 'object': measurement})


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class MeasurementDeleteView(View):
    def get(self, request, pk):
        measurement = get_object_or_404(AirQualityData, pk=pk)
        return render(request, 'airquality/confirm_delete.html', {'object': measurement, 'type': 'mesure'})

    def post(self, request, pk):
        measurement = get_object_or_404(AirQualityData, pk=pk)
        measurement.delete()
        messages.success(request, 'Mesure supprimée.')
        return redirect('airquality:admin_dashboard')


# --- Pollutant CRUD ---

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class PollutantCreateView(View):
    def get(self, request):
        form = PollutantForm()
        return render(request, 'airquality/pollutant_form.html', {'form': form, 'action': 'Ajouter'})

    def post(self, request):
        form = PollutantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Polluant ajouté avec succès.')
            return redirect('airquality:admin_dashboard')
        return render(request, 'airquality/pollutant_form.html', {'form': form, 'action': 'Ajouter'})


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class PollutantUpdateView(View):
    def get(self, request, pk):
        pollutant = get_object_or_404(Pollutant, pk=pk)
        form = PollutantForm(instance=pollutant)
        return render(request, 'airquality/pollutant_form.html', {'form': form, 'action': 'Modifier', 'object': pollutant})

    def post(self, request, pk):
        pollutant = get_object_or_404(Pollutant, pk=pk)
        form = PollutantForm(request.POST, instance=pollutant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Polluant modifié avec succès.')
            return redirect('airquality:admin_dashboard')
        return render(request, 'airquality/pollutant_form.html', {'form': form, 'action': 'Modifier', 'object': pollutant})


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class PollutantDeleteView(View):
    def get(self, request, pk):
        pollutant = get_object_or_404(Pollutant, pk=pk)
        return render(request, 'airquality/confirm_delete.html', {'object': pollutant, 'type': 'polluant'})

    def post(self, request, pk):
        pollutant = get_object_or_404(Pollutant, pk=pk)
        pollutant.delete()
        messages.success(request, 'Polluant supprimé.')
        return redirect('airquality:admin_dashboard')


# --- Evaluation moderation (admin) ---

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class EvaluationToggleView(View):
    def post(self, request, pk):
        evaluation = get_object_or_404(Evaluation, pk=pk)
        evaluation.is_approved = not evaluation.is_approved
        evaluation.save()
        return redirect('airquality:admin_dashboard')


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class EvaluationDeleteView(View):
    def post(self, request, pk):
        evaluation = get_object_or_404(Evaluation, pk=pk)
        evaluation.delete()
        messages.success(request, 'Évaluation supprimée.')
        return redirect('airquality:admin_dashboard')


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

class APIStationDataView(View):
    """API pour obtenir les données d'une station"""
    def get(self, request, station_id):
        try:
            station = MeasurementStation.objects.get(pk=station_id)
            measurements = AirQualityData.objects.filter(
                station=station,
                measurement_date__gte=timezone.now() - timedelta(days=7)
            ).select_related('pollutant')
            data = {
                'station': {
                    'id': station.id,
                    'name': station.name,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                },
                'measurements': [
                    {
                        'pollutant': m.pollutant.symbol,
                        'value': m.value,
                        'unit': m.unit,
                        'date': m.measurement_date.isoformat(),
                    }
                    for m in measurements
                ]
            }
            return JsonResponse(data)
        except MeasurementStation.DoesNotExist:
            return JsonResponse({'error': 'Station not found'}, status=404)


class APILatestDataView(View):
    """API JSON — 10 dernières mesures (pour polling live)"""
    def get(self, request):
        measurements = AirQualityData.objects.select_related(
            'station', 'pollutant'
        ).order_by('-measurement_date')[:10]

        data = [
            {
                'station': m.station.name,
                'pollutant': m.pollutant.symbol,
                'value': round(m.value, 1),
                'unit': m.unit,
                'limit_oms': round(m.pollutant.limit_oms, 1),
                'date': m.measurement_date.strftime('%d/%m/%Y %H:%M'),
                'over_limit': m.value > m.pollutant.limit_oms,
            }
            for m in measurements
        ]
        return JsonResponse({'measurements': data, 'count': len(data)})


class APIPollutantStatsView(View):
    """API JSON — statistiques par polluant (pour polling live)"""
    def get(self, request):
        pollutants = Pollutant.objects.all()
        stats = []
        for p in pollutants:
            qs = AirQualityData.objects.filter(
                pollutant=p,
                is_valid=True,
                measurement_date__gte=timezone.now() - timedelta(days=365)
            )
            if qs.exists():
                agg = qs.aggregate(
                    avg_value=Avg('value'),
                    max_value=Max('value'),
                    min_value=Min('value'),
                    total_count=Count('id')
                )
                stats.append({
                    'symbol': p.symbol,
                    'name': p.name,
                    'avg': round(agg['avg_value'], 1) if agg['avg_value'] else 0,
                    'max': round(agg['max_value'], 1) if agg['max_value'] else 0,
                    'min': round(agg['min_value'], 1) if agg['min_value'] else 0,
                    'count': agg['total_count'],
                })
        return JsonResponse({'stats': stats})


