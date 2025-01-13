from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='APIKL',
    version='1.2',
    author='Vitaly_Kalinsky',
    author_email='kalinskyvii@gmail.com',
    description='This module allows you to find API keys and passwords in your project.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/VitalyKalinsky/APIKL',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='API keys APIkeys locate detect passwords',
    project_urls={
        'GitHub': 'https://github.com/VitalyKalinsky'
    },
    python_requires='>=3.12.2'
)
