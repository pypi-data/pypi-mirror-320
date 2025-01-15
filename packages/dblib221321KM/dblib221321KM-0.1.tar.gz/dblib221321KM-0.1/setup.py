from setuptools import setup, find_packages

setup(
    name='dblib221321KM',          # Название
    version='0.1',
    packages=find_packages(),
    install_requires=['psycopg2'],
    author='Name',           # Имя
    author_email='your.email@example.com',  # Email
    description='A library for interacting with a PostgreSQL database',  # Описание
    url='https://github.com/yourusername/dblib221321KM',  # Ссылка на репозиторий на гите
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)