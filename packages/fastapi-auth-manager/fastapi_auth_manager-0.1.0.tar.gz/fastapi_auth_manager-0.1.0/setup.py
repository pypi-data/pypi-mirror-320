from setuptools import setup, find_packages

setup(
    name='fastapi_auth_manager',
    version='0.1.0',
    description='A simple authentication management library for FastAPI',
    author='Mirzonabot Mirzonabotov',
    author_email='mirzonabot.mirzonabotov99@gmail.com',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'python-jose',
        'passlib[bcrypt]',
        'pydantic',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
