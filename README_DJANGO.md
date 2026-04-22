# AirWatch Europe - Django with MySQL

Application web Django pour la surveillance de la qualité de l'air en Europe.

## 🚀 Quick Start

### 1. Installation des dépendances Python
```bash
pip install -r requirements.txt
```

### 2. Créer la base de données MySQL
```sql
CREATE DATABASE airwatch_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON airwatch_db.* TO 'airwatch_user'@'localhost' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;
```

### 3. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos paramètres MySQL
```

### 4. Migrations Django
```bash
python manage.py migrate
```

### 5. Remplir la base de données
```bash
# Données de base
python manage.py populate_data

# Avec données de mesure générées (7 jours)
python manage.py populate_data --full
```

### 6. Créer un admin (optionnel)
```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur
```bash
python manage.py runserver
```

Accédez à: **http://localhost:8000**

## 📊 Commandes disponibles

```bash
# Remplir la base de données
python manage.py populate_data [--full]

# Récupérer données OpenAQ (temps réel)
python manage.py fetch_openaq_data [--city <name>] [--country <code>]

# Admin interface
python manage.py createsuperuser

# Serveur accessible en réseau
python manage.py runserver 0.0.0.0:8000

# Générer fichiers statiques
python manage.py collectstatic
```

## 🗂️ Structure

- **airwatch_project/** - Configuration principale
  - settings.py - Base de données MySQL, apps
  - urls.py - Routes
  
- **airquality/** - App Django
  - models.py - 8 modèles (Pollutants, Countries, Cities, Stations, Air Quality Data, Health Impacts, Data Sources)
  - views.py - 7 vues + API
  - management/commands/ - Scripts de gestion
  
- **templates/** - Templates HTML/Django
- **static/** - CSS, JS, images

## 📐 Modèles de données

1. **Pollutant** - Polluant (PM2.5, PM10, NO2, O3, SO2, CO)
2. **Country** - Pays européen
3. **City** - Ville avec coordonnées GPS
4. **MeasurementStation** - Station de mesure
5. **AirQualityData** - Mesures (valeur, date, validité)
6. **HealthImpact** - Impacts sanitaires par polluant
7. **DataSource** - Référence aux sources (EEA, Copernicus, OpenAQ)

## 🔑 Fonctionnalités

✅ Gestion complète des données de qualité de l'air
✅ Base de données MySQL avec 7 modèles
✅ Administration Django
✅ API JSON pour récupérer les données
✅ Carte interactive (Leaflet.js)
✅ Intégration OpenAQ API
✅ Générateur de données pour développement
✅ Templates responsifs

## ⚙️ Configuration MySQL

Éditer `.env` :

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=airwatch_db
DB_USER=airwatch_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=3306
```

## 🌐 URLs disponibles

- `/` - Accueil
- `/data/` - Données et statistiques
- `/map/` - Carte interactive
- `/impacts/` - Impacts sanitaires
- `/sources/` - Sources de données
- `/city/<id>/` - Détails d'une ville
- `/api/station/<id>/data/` - API JSON
- `/admin/` - Interface d'administration

## 📝 Notes importantes

- Les données générées par `populate_data --full` sont aléatoires pour le développement
- L'API OpenAQ est limitée à 10 requêtes/minute
- Les migrations Django gèrent la structure MySQL
- Collectez les statiques avant le déploiement production

## 🚀 Déploiement

Pour la production :

1. Set `DEBUG=False` dans `.env`
2. Changez la `SECRET_KEY`
3. Collectez les statiques : `python manage.py collectstatic`
4. Utilisez un serveur WSGI (gunicorn, uWSGI, etc.)
5. Configurez un reverse proxy (Nginx, Apache)
6. Utilisez HTTPS

Plateformes recommandées : Heroku, PythonAnywhere, AWS, DigitalOcean, Azure

## 📚 Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [EEA Air Quality Data](https://www.eea.europa.eu/data-and-maps/data/aqereporting-9)
- [OpenAQ API](https://openaq.org/)
- [Copernicus CAMS](https://atmosphere.copernicus.eu/)
