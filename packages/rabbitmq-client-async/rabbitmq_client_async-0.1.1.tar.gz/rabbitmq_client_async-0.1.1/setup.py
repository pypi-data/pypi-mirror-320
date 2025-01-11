from setuptools import find_packages
from setuptools import setup


setup(
    name='rabbitmq-client-async',
    version='0.1.1',
    description='Universal RabbitMQ client for Python microservices',
    author='Stanislav',
    author_email='nstanislass@gmail.com',
    packages=find_packages(),
    install_requires=[
        'aio_pika>=9.5.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
