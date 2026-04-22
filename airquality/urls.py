from django.urls import path
from . import views

app_name = 'airquality'

urlpatterns = [
    # Public pages
    path('', views.IndexView.as_view(), name='index'),
    path('data/', views.DataView.as_view(), name='data'),
    path('map/', views.MapView.as_view(), name='map'),
    path('impacts/', views.ImpactsView.as_view(), name='impacts'),
    path('sources/', views.SourcesView.as_view(), name='sources'),
    path('city/<int:city_id>/', views.CityDetailView.as_view(), name='city_detail'),
    path('evaluations/', views.EvaluationsView.as_view(), name='evaluations'),

    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Admin dashboard
    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),

    # City CRUD
    path('admin-panel/cities/add/', views.CityCreateView.as_view(), name='city_add'),
    path('admin-panel/cities/<int:city_id>/edit/', views.CityUpdateView.as_view(), name='city_edit'),
    path('admin-panel/cities/<int:city_id>/delete/', views.CityDeleteView.as_view(), name='city_delete'),

    # Measurement CRUD
    path('admin-panel/measurements/add/', views.MeasurementCreateView.as_view(), name='measurement_add'),
    path('admin-panel/measurements/<int:pk>/edit/', views.MeasurementUpdateView.as_view(), name='measurement_edit'),
    path('admin-panel/measurements/<int:pk>/delete/', views.MeasurementDeleteView.as_view(), name='measurement_delete'),

    # Pollutant CRUD
    path('admin-panel/pollutants/add/', views.PollutantCreateView.as_view(), name='pollutant_add'),
    path('admin-panel/pollutants/<int:pk>/edit/', views.PollutantUpdateView.as_view(), name='pollutant_edit'),
    path('admin-panel/pollutants/<int:pk>/delete/', views.PollutantDeleteView.as_view(), name='pollutant_delete'),

    # Evaluation moderation
    path('admin-panel/evaluations/<int:pk>/toggle/', views.EvaluationToggleView.as_view(), name='evaluation_toggle'),
    path('admin-panel/evaluations/<int:pk>/delete/', views.EvaluationDeleteView.as_view(), name='evaluation_delete'),

    # API endpoints
    path('api/station/<int:station_id>/data/', views.APIStationDataView.as_view(), name='api_station_data'),
    path('api/latest/', views.APILatestDataView.as_view(), name='api_latest'),
    path('api/pollutant-stats/', views.APIPollutantStatsView.as_view(), name='api_pollutant_stats'),
]
