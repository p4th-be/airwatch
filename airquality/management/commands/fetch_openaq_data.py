from django.core.management.base import BaseCommand
from datetime import datetime
import time
import requests
from django.utils import timezone
from airquality.models import AirQualityData, MeasurementStation, Pollutant, City


class Command(BaseCommand):
    help = 'Fetch air quality data from OpenAQ API and update the local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--city',
            type=str,
            help='Filter by city name',
        )
        parser.add_argument(
            '--country',
            type=str,
            help='Filter by country code',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Number of records to request per city',
        )
        parser.add_argument(
            '--loop',
            action='store_true',
            help='Run the fetch command continuously every interval',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Interval in seconds between fetches when using --loop',
        )

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from OpenAQ API...')

        city_filter = options.get('city')
        country_filter = options.get('country')
        limit = options.get('limit', 1000)
        loop = options.get('loop', False)
        interval = options.get('interval', 60)

        if city_filter:
            cities = City.objects.filter(name__iexact=city_filter)
            if not cities.exists():
                self.stdout.write(self.style.WARNING(f'No city found with name {city_filter}'))
                return
        elif country_filter:
            cities = City.objects.filter(country__code__iexact=country_filter)
            if not cities.exists():
                self.stdout.write(self.style.WARNING(f'No cities found for country code {country_filter}'))
                return
        else:
            cities = City.objects.all()

        while True:
            total_count = 0
            for city in cities:
                self.stdout.write(self.style.NOTICE(f'Fetching data for city: {city.name} ({city.country.code})'))
                count = self.fetch_city_data(city, limit)
                total_count += count
                self.stdout.write(self.style.SUCCESS(f'  → Stored {count} measurements for {city.name}'))

            self.stdout.write(self.style.SUCCESS(f'✓ Total measurements stored: {total_count}'))

            if not loop:
                break

            self.stdout.write(self.style.NOTICE(f'Waiting {interval} seconds before next fetch...'))
            time.sleep(interval)

    def fetch_city_data(self, city, limit):
        base_url = 'https://api.openaq.org/v2/latest'
        params = {
            'limit': limit,
            'city': city.name,
            'country': city.country.code,
        }

        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error fetching OpenAQ data for {city.name}: {e}'))
            return 0

        if 'results' not in data or not data['results']:
            self.stdout.write(self.style.WARNING(f'No results from OpenAQ for {city.name}'))
            return 0

        count = 0
        for result in data['results']:
            count += self.process_result(city, result)

        return count

    def process_result(self, city, result):
        count = 0
        location_name = result.get('location', 'Unknown Station')
        coordinates = result.get('coordinates', {})
        latitude = coordinates.get('latitude')
        longitude = coordinates.get('longitude')

        station = MeasurementStation.objects.filter(name__iexact=location_name).first()
        if not station:
            station = MeasurementStation.objects.filter(city=city, latitude=latitude, longitude=longitude).first()

        if not station:
            station = MeasurementStation.objects.create(
                name=f'{city.name} - {location_name}',
                city=city,
                latitude=latitude if latitude is not None else city.latitude,
                longitude=longitude if longitude is not None else city.longitude,
                altitude=0,
                is_active=True,
            )

        for measurement in result.get('measurements', []):
            parameter = measurement.get('parameter', '').upper()
            value = measurement.get('value')
            unit = measurement.get('unit', '')
            measured_at = measurement.get('lastUpdated') or measurement.get('date', {}).get('utc')

            pollutant = self.get_pollutant_from_parameter(parameter)
            if not pollutant or value is None:
                continue

            measurement_date = self.parse_date(measured_at)
            if not measurement_date:
                measurement_date = timezone.now()

            # Ne pas écraser les données modifiées manuellement via l'admin
            if not AirQualityData.objects.filter(
                station=station,
                pollutant=pollutant,
                measurement_date=measurement_date,
                manually_edited=True,
            ).exists():
                AirQualityData.objects.update_or_create(
                    station=station,
                    pollutant=pollutant,
                    measurement_date=measurement_date,
                    defaults={
                        'value': value,
                        'unit': unit or pollutant.unit,
                        'is_valid': True,
                    }
                )
            count += 1

        return count

    def get_pollutant_from_parameter(self, parameter):
        param_map = {
            'PM25': 'PM25',
            'PM2.5': 'PM25',
            'PM10': 'PM10',
            'NO2': 'NO2',
            'O3': 'O3',
            'SO2': 'SO2',
            'CO': 'CO',
        }
        symbol = param_map.get(parameter)
        if not symbol:
            return None

        return Pollutant.objects.filter(symbol=symbol).first()

    def parse_date(self, value):
        if not value:
            return None

        try:
            if isinstance(value, str):
                if value.endswith('Z'):
                    value = value[:-1] + '+00:00'
                return datetime.fromisoformat(value)
        except ValueError:
            return None

        return None
