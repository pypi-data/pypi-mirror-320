from setuptools import setup, find_packages

setup(
   name='my_unique_rocket20',
   version='1.0.0',
   author='Chaib Fakhreddine',
   author_email='fakhreddin.fouzi@gmail.com',
   packages=find_packages(),  # Recherche automatiquement les packages
   url='http://pypi.python.org/pypi/rocket20/',
   license='LICENSE.txt',
   description='An awesome package that does something',
   long_description=open('README.md').read(),
   long_description_content_type="text/markdown",
   install_requires=[]  # Ajoutez des dépendances ici si nécessaire
)
