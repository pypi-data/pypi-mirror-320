from setuptools import setup, find_packages


setup(
    name="tarea4-ASG",
    version="0.1.0",
    author="Alberto Serradilla Gutiérrez",
    author_email="aserradillag01@educastillalamancha.es",
    description="Aplicación de reservas con interfaz gráfica",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True, 
     package_data={ 
        'tarea3.Recursos': ['img/*.jpeg', 'img/*.png'], 
        'tarea3.Modelo': ['*.db', '*.sql'],
        'tarea3.Vistas': ['*.ui'], 
    },
    install_requires=[
        'PySide6>=6.8.1', 
    ],
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "tarea4=tarea3.principal:main",
        ],
    },
)
