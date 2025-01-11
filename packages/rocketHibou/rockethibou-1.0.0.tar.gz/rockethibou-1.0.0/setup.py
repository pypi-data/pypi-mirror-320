from setuptools import setup

setup(
   name='rocketHibou',  # Nom unique du package
   version='1.0.0',       # Numéro de version
   author='HibetElrahmane',    # Remplacez par votre nom
   author_email='he.ouchene@esi-sba.dz',  # Remplacez par votre e-mail
   packages=['rocketHibou'],  # Assurez-vous que ce dossier existe
   url='https://github.com/votre-repo/rocketHibou',  # Remplacez par l'URL de votre projet (si disponible)
   license='MIT',         # Remplacez par le type de licence utilisé (exemple : MIT)
   description='An awesome package that does something useful.',  # Description courte
   long_description=open('README.md').read(),  # Assurez-vous que README.md existe
   long_description_content_type="text/markdown",  # Format du long_description
   install_requires=[      # Liste des dépendances externes
       # Ajoutez ici les bibliothèques nécessaires, par ex. :
       'numpy',
       'pandas'
   ],
)
