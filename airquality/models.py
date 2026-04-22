from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Pollutant(models.Model):
    """Modèle pour les polluants surveillés"""
    SYMBOLS = [
        ('PM25', 'PM₂.₅'),
        ('PM10', 'PM₁₀'),
        ('NO2', 'NO₂'),
        ('O3', 'O₃'),
        ('SO2', 'SO₂'),
        ('CO', 'CO'),
    ]
    
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, choices=SYMBOLS, unique=True)
    description = models.TextField()
    limit_oms = models.FloatField(help_text="Limite OMS en μg/m³")
    limit_eu = models.FloatField(null=True, blank=True, help_text="Limite UE en μg/m³")
    unit = models.CharField(max_length=20, default='μg/m³')
    manually_edited = models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Pollutants"
        ordering = ['symbol']
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"


class Country(models.Model):
    """Modèle pour les pays européens"""
    code = models.CharField(max_length=2, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    population = models.IntegerField(default=0)
    manually_edited = models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class City(models.Model):
    """Modèle pour les villes européennes"""
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    latitude = models.FloatField()
    longitude = models.FloatField()
    population = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    manually_edited = models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.country}"


class MeasurementStation(models.Model):
    """Modèle pour les stations de mesure"""
    name = models.CharField(max_length=150)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='stations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.IntegerField(default=0, help_text="Altitude en mètres")
    is_active = models.BooleanField(default=True)
    manually_edited = models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Measurement Station"
    
    def __str__(self):
        return f"{self.name} ({self.city})"


class AirQualityData(models.Model):
    """Modèle pour les mesures de qualité de l'air"""
    station = models.ForeignKey(MeasurementStation, on_delete=models.CASCADE, related_name='measurements')
    pollutant = models.ForeignKey(Pollutant, on_delete=models.CASCADE, related_name='measurements')
    value = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='μg/m³')
    measurement_date = models.DateTimeField()
    is_valid = models.BooleanField(default=True)
    manually_edited = models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Air Quality Data"
        ordering = ['-measurement_date']
        indexes = [
            models.Index(fields=['station', 'measurement_date']),
            models.Index(fields=['pollutant', 'measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.pollutant.symbol} - {self.station.name} ({self.measurement_date})"


class HealthImpact(models.Model):
    """Modèle pour les impacts sanitaires des polluants"""
    pollutant = models.ForeignKey(Pollutant, on_delete=models.CASCADE, related_name='health_impacts')
    disease = models.CharField(max_length=150)
    description = models.TextField()
    annual_deaths_europe = models.IntegerField(default=0, help_text="Décès estimés annuels en Europe")
    vulnerable_groups = models.TextField(help_text="Groupes vulnérables, séparés par des virgules")
    manually_edited = models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Health Impacts"
        ordering = ['pollutant']
    
    def __str__(self):
        return f"{self.disease} (exposed to {self.pollutant.symbol})"


class DataSource(models.Model):
    """Modèle pour les sources de données"""
    SOURCE_TYPES = [
        ('EEA', 'European Environment Agency'),
        ('COPERNICUS', 'Copernicus CAMS'),
        ('OPENAQ', 'OpenAQ'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    url = models.URLField()
    description = models.TextField()
    manually_edited = models.BooleanField(default=False, help_text="Modifié manuellement via l'admin – protège contre les mises à jour automatiques")
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Evaluation(models.Model):
    """Évaluations soumises par les utilisateurs"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    author_name = models.CharField(max_length=100)
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Evaluations"

    def __str__(self):
        return f"Évaluation {self.rating}/5 par {self.author_name}"
