from setuptools import setup, find_packages

setup(
    name='coScout',
    version='0.1',
    author='Yangming Huang',
    description='A tiny agent to send data to coScene data platform',
    url='https://github.com/coscene-io/sample-json-api-files',
    keywords='data, agent, upload, daemon.py',
    python_requires='>=2.7, <3',
    packages=find_packages(include=['cos']),
    package_data={
        # all .dat files at any package depth
        '': ['gs/*'],
    },
    install_requires=[
        'certifi==2021.10.8',
        'pathlib2~=2.3.7.post1',
        'requests~=2.27.1',
        'scandir~=1.10.0',
        'setuptools~=44.1.1',
        'six~=1.16.0',
        'tqdm~=4.64.1',
        'strictyaml==1.4.4',
    ],
    entry_points={
        'console_scripts': [
            'cos=cos:main',
        ]
    }
)
