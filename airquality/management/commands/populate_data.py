from django.core.management.base import BaseCommand
from django.utils import timezone
from airquality.models import (
    Pollutant, Country, City, MeasurementStation,
    AirQualityData, HealthImpact, DataSource
)
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populate database with initial data for AirWatch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Generate full dataset including measurements',
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting data generation...")

        # Create Pollutants
        self.create_pollutants()
        self.stdout.write(self.style.SUCCESS('✓ Pollutants created'))

        # Create Data Sources
        self.create_data_sources()
        self.stdout.write(self.style.SUCCESS('✓ Data sources created'))

        # Create Countries
        self.create_countries()
        self.stdout.write(self.style.SUCCESS('✓ Countries created'))

        # Create Cities
        self.create_cities()
        self.stdout.write(self.style.SUCCESS('✓ Cities created'))

        # Create Measurement Stations
        self.create_measurement_stations()
        self.stdout.write(self.style.SUCCESS('✓ Measurement stations created'))

        # Create Health Impacts
        self.create_health_impacts()
        self.stdout.write(self.style.SUCCESS('✓ Health impacts created'))

        if options['full']:
            # Generate measurements
            self.generate_measurements()
            self.stdout.write(self.style.SUCCESS('✓ Measurement data generated'))

        self.stdout.write(self.style.SUCCESS('\n✓ Data generation completed!'))

    def create_pollutants(self):
        """Create pollutant records"""
        pollutants_data = [
            {
                'name': 'Particules fines',
                'symbol': 'PM25',
                'description': 'Particules < 2.5 μm. Pénètrent dans les alvéoles pulmonaires et atteignent la circulation sanguine.',
                'limit_oms': 5.0,
                'limit_eu': 25.0,
            },
            {
                'name': 'Particules grossières',
                'symbol': 'PM10',
                'description': 'Particules < 10 μm. Poussières, pollens, combustion.',
                'limit_oms': 15.0,
                'limit_eu': 40.0,
            },
            {
                'name': 'Dioxyde d\'azote',
                'symbol': 'NO2',
                'description': 'Polluant gazeux provenant du trafic automobile et des installations industrielles.',
                'limit_oms': 10.0,
                'limit_eu': 40.0,
            },
            {
                'name': 'Ozone troposphérique',
                'symbol': 'O3',
                'description': 'Polluant secondaire formé par les réactions chimiques en présence du soleil.',
                'limit_oms': 60.0,
                'limit_eu': 120.0,
            },
            {
                'name': 'Dioxyde de soufre',
                'symbol': 'SO2',
                'description': 'Produit par la combustion de carburants contenant du soufre.',
                'limit_oms': 15.0,
                'limit_eu': 125.0,
            },
            {
                'name': 'Monoxyde de carbone',
                'symbol': 'CO',
                'description': 'Gaz inodore et incolore provenant de la combustion incomplète.',
                'limit_oms': 4000.0,
                'limit_eu': 10000.0,
            },
        ]

        for data in pollutants_data:
            Pollutant.objects.get_or_create(
                symbol=data['symbol'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'limit_oms': data['limit_oms'],
                    'limit_eu': data.get('limit_eu'),
                }
            )

    def create_data_sources(self):
        """Create data source records"""
        sources_data = [
            {
                'name': 'European Environment Agency (EEA)',
                'source_type': 'EEA',
                'url': 'https://www.eea.europa.eu/data-and-maps/data/aqereporting-9',
                'description': 'Agence Européenne pour l\'Environnement - Base AirBase avec 2500+ stations de mesure',
            },
            {
                'name': 'Copernicus Atmosphere Monitoring Service',
                'source_type': 'COPERNICUS',
                'url': 'https://atmosphere.copernicus.eu/',
                'description': 'Données satellitaires et prévisions de qualité de l\'air 4 jours',
            },
            {
                'name': 'OpenAQ',
                'source_type': 'OPENAQ',
                'url': 'https://openaq.org/',
                'description': 'API ouverte avec données temps réel de qualité de l\'air',
            },
        ]

        for data in sources_data:
            DataSource.objects.get_or_create(
                name=data['name'],
                defaults={
                    'source_type': data['source_type'],
                    'url': data['url'],
                    'description': data['description'],
                }
            )

    def create_countries(self):
        """Create European countries"""
        countries_data = [
            {'code': 'FR', 'name': 'France', 'region': 'Western Europe', 'population': 68000000},
            {'code': 'DE', 'name': 'Germany', 'region': 'Central Europe', 'population': 84000000},
            {'code': 'PL', 'name': 'Poland', 'region': 'Central Europe', 'population': 38000000},
            {'code': 'IT', 'name': 'Italy', 'region': 'Southern Europe', 'population': 58000000},
            {'code': 'ES', 'name': 'Spain', 'region': 'Southern Europe', 'population': 48000000},
            {'code': 'NL', 'name': 'Netherlands', 'region': 'Western Europe', 'population': 18000000},
            {'code': 'GB', 'name': 'United Kingdom', 'region': 'Western Europe', 'population': 67000000},
            {'code': 'SE', 'name': 'Sweden', 'region': 'Northern Europe', 'population': 10000000},
            {'code': 'CZ', 'name': 'Czech Republic', 'region': 'Central Europe', 'population': 10500000},
            {'code': 'AT', 'name': 'Austria', 'region': 'Central Europe', 'population': 9000000},
        ]

        for data in countries_data:
            Country.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'region': data['region'],
                    'population': data['population'],
                }
            )

    def create_cities(self):
        """Create major European cities"""
        cities_data = [
            {'name': 'Paris', 'country_code': 'FR', 'lat': 48.8566, 'lon': 2.3522, 'pop': 2165423},
            {'name': 'Berlin', 'country_code': 'DE', 'lat': 52.5200, 'lon': 13.4050, 'pop': 3644826},
            {'name': 'Varsovie', 'country_code': 'PL', 'lat': 52.2297, 'lon': 21.0122, 'pop': 1863582},
            {'name': 'Rome', 'country_code': 'IT', 'lat': 41.9028, 'lon': 12.4964, 'pop': 2761477},
            {'name': 'Madrid', 'country_code': 'ES', 'lat': 40.4168, 'lon': -3.7038, 'pop': 3223334},
            {'name': 'Amsterdam', 'country_code': 'NL', 'lat': 52.3676, 'lon': 4.9041, 'pop': 873555},
            {'name': 'Londres', 'country_code': 'GB', 'lat': 51.5074, 'lon': -0.1278, 'pop': 9002488},
            {'name': 'Stockholm', 'country_code': 'SE', 'lat': 59.3293, 'lon': 18.0686, 'pop': 975551},
            {'name': 'Prague', 'country_code': 'CZ', 'lat': 50.0755, 'lon': 14.4378, 'pop': 1365581},
            {'name': 'Vienne', 'country_code': 'AT', 'lat': 48.2082, 'lon': 16.3738, 'pop': 1920000},
        ]

        for data in cities_data:
            country = Country.objects.get(code=data['country_code'])
            City.objects.get_or_create(
                name=data['name'],
                country=country,
                defaults={
                    'latitude': data['lat'],
                    'longitude': data['lon'],
                    'population': data['pop'],
                    'description': f"Ville de {data['name']} - Surveillance de la qualité de l'air",
                }
            )

    def create_measurement_stations(self):
        """Create measurement stations for each city"""
        cities = City.objects.all()
        
        for city in cities:
            # Create 2-3 stations per city
            for i in range(random.randint(2, 3)):
                station_name = f"{city.name} - Station {i+1}"
                # Add slight variations to coordinates
                lat = city.latitude + random.uniform(-0.01, 0.01)
                lon = city.longitude + random.uniform(-0.01, 0.01)
                
                MeasurementStation.objects.get_or_create(
                    name=station_name,
                    city=city,
                    defaults={
                        'latitude': lat,
                        'longitude': lon,
                        'altitude': random.randint(0, 500),
                        'is_active': True,
                    }
                )

    def create_health_impacts(self):
        """Create health impact data"""
        impacts_data = [
            {
                'symbol': 'PM25',
                'disease': 'Maladies cardiovasculaires',
                'description': 'Les particules fines pénètrent dans la circulation sanguine, causant des problèmes cardiaques.',
                'deaths': 280000,
                'vulnerable': 'Personnes âgées, enfants, patients cardiaques',
            },
            {
                'symbol': 'PM25',
                'disease': 'Cancer du poumon',
                'description': 'Exposition chronique aux PM2.5 augmente le risque de cancer pulmonaire.',
                'deaths': 110000,
                'vulnerable': 'Fumeurs, travailleurs exposés',
            },
            {
                'symbol': 'PM10',
                'disease': 'Maladies respiratoires chroniques',
                'description': 'Irritation et inflammation des voies respiratoires.',
                'deaths': 40000,
                'vulnerable': 'Asthmatiques, patients BPCO',
            },
            {
                'symbol': 'NO2',
                'disease': 'Asthme',
                'description': 'Le dioxyde d\'azote augmente les symptômes et les crises d\'asthme.',
                'deaths': 5000,
                'vulnerable': 'Enfants, asthmatiques',
            },
            {
                'symbol': 'O3',
                'disease': 'Problèmes respiratoires aigus',
                'description': 'L\'ozone troposphérique cause une inflammation des voies respiratoires.',
                'deaths': 12000,
                'vulnerable': 'Enfants, personnes âgées, sportifs',
            },
        ]

        for data in impacts_data:
            pollutant = Pollutant.objects.get(symbol=data['symbol'])
            HealthImpact.objects.get_or_create(
                pollutant=pollutant,
                disease=data['disease'],
                defaults={
                    'description': data['description'],
                    'annual_deaths_europe': data['deaths'],
                    'vulnerable_groups': data['vulnerable'],
                }
            )

    def generate_measurements(self):
        """Generate random measurement data for the past 365 days"""
        self.stdout.write("Generating measurement data (this may take a moment)...")
        
        stations = MeasurementStation.objects.all()
        pollutants = Pollutant.objects.all()
        
        # Generate one measurement per station per pollutant per day for the past 30 days
        for station in stations:
            for pollutant in pollutants:
                for days_ago in range(30):
                    measurement_date = timezone.now() - timedelta(days=days_ago)
                    
                    # Generate realistic values based on pollutant limits
                    if pollutant.symbol == 'PM25':
                        value = random.uniform(5, 50)
                    elif pollutant.symbol == 'PM10':
                        value = random.uniform(10, 80)
                    elif pollutant.symbol == 'NO2':
                        value = random.uniform(10, 100)
                    elif pollutant.symbol == 'O3':
                        value = random.uniform(20, 150)
                    elif pollutant.symbol == 'SO2':
                        value = random.uniform(5, 50)
                    else:  # CO
                        value = random.uniform(200, 1000)
                    
                    AirQualityData.objects.get_or_create(
                        station=station,
                        pollutant=pollutant,
                        measurement_date=measurement_date.replace(hour=random.randint(0, 23)),
                        defaults={
                            'value': value,
                            'is_valid': random.random() > 0.1,  # 90% validity
                        }
                    )
