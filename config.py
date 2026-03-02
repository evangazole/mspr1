# Configuration base de données PostgreSQL
# À adapter selon votre environnement

# Connexion PostgreSQL
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mspr1_aura"
DB_USER = "postgres"
DB_PASSWORD = "votre_mot_de_passe"  # À remplacer

# Chaîne de connexion SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Chemins fichiers
PATH_DATA_RAW = "./data/raw/"
PATH_DATA_PROCESSED = "./data/processed/"
PATH_SCRIPTS = "./scripts/"
PATH_SQL = "./sql/"
PATH_RAPPORTS = "./rapports/"

# Paramètres modélisation
RANDOM_STATE = 42
TEST_SIZE = 0.2
VALIDATION_K_FOLD = 5

# Paramètres Random Forest
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 15
RF_MIN_SAMPLES_SPLIT = 5
RF_MIN_SAMPLES_LEAF = 2

# Paramètres K-Means
KMEANS_N_CLUSTERS = 4
KMEANS_RANDOM_STATE = 42

# Années données
MIN_YEAR = 2017
MAX_YEAR = 2022

# Département AURA (codes INSEE)
AURA_DEPARTMENTS = [
    "01",  # Ain
    "03",  # Allier
    "07",  # Ardèche
    "15",  # Cantal
    "26",  # Drôme
    "38",  # Isère
    "42",  # Loire
    "43",  # Haute-Loire
    "63",  # Puy-de-Dôme
    "69",  # Rhône
    "73",  # Savoie
    "74"   # Haute-Savoie
]
