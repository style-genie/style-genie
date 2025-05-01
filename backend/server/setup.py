from setuptools import setup, find_packages

setup(
    name='stylegenie',
    version='0.1.0',
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    install_requires=[
        'python-dotenv==1.1.0',
        'fastapi<0.114.0,>=0.113.0',
        'pydantic<3.0.0,>=2.7.0',
        'uvicorn==0.34.0',
        'python-multipart==0.0.20',
        'openai==1.76.0',
        'litellm==1.67.5',
    ],
   entry_points={
        'console_scripts': [
            'stylegenie=main:main',
        ],
    },
)
