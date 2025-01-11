from setuptools import setup, find_packages

setup(
    name='rabbiteer',  # El nombre de tu paquete
    version='0.1.1',    # La versión de tu paquete
    author='Sebastian Sala',  # Tu nombre o el del autor
    author_email='sebastian.sala.alanis@gmail.com',  # Tu email
    description='A friendly and robust RabbitMQ client library for Python',  # Descripción corta del paquete
    long_description=open('README.md').read(),  # Descripción más extensa (por lo general desde un README)
    long_description_content_type='text/markdown',  # Tipo de formato para la descripción larga
    url='https://github.com/usuario/mi_paquete',  # URL del repositorio o sitio de proyecto
    packages=find_packages(),  # Encuentra automáticamente todos los paquetes en tu proyecto
    classifiers=[  # Clasificadores estándar de PyPI para que sea más fácil de encontrar
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[  # Dependencias del paquete
        'requests>=2.0',
        'numpy>=1.18',
    ],
    python_requires='>=3.6',  # Versión mínima de Python
    include_package_data=True,  # Asegúrate de incluir archivos adicionales (definidos en MANIFEST.in)
)
