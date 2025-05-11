# core/__init__.py

import cloudinary
from django.conf import settings

# Só aqui, depois de o settings já estarem carregados:
cloudinary.config(**settings.CLOUDINARY)