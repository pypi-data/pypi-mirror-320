import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.1' 
PACKAGE_NAME = 'corazaytubos_sim' #Debe coincidir con el nombre de la carpeta 
AUTHOR = 'Isaac Josué Chávez Martínez & Heber Mercado Martínez' 
AUTHOR_EMAIL = 'isaacj.ch.m@gmail.com' 
URL = 'https://www.linkedin.com/in/isaac-chavez-analisisdedatatos-bigdata-automatizacion/' #Perfil de LinkedIn

LICENSE = 'MIT' #Tipo de licencia
DESCRIPTION = 'Librería para realizar simulaciones de un intercambiador de calor de coraza y tubos.' #Descripción corta
LONG_DESCRIPTION = (HERE / "Readme.md").read_text(encoding='utf-8') #Referencia al documento README con una descripción más elaborada
LONG_DESC_TYPE = "text/markdown"


#Paquetes necesarios para que funcione la libreía. Se instalarán a la vez si no lo tuvieras ya instalado
INSTALL_REQUIRES = [
      'pandas==1.5.2',
      'thermo==0.3.0'
      ]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)