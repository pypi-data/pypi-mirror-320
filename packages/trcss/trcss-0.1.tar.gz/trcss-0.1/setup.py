from setuptools import setup, find_packages

setup(
    name='trcss',
    version='0.1',
    packages=find_packages(),
    description='Ajax 6.0.0 Beta 3 Font İndirmenize Kolaylık Sağlar',
    author='Atilla',
    author_email='your_email@gmail.com',  # Kendi email adresinizi ekleyin
    url='https://github.com/',  # Kendi repo adresinizi ekleyin
    entry_points={
        'console_scripts': [
            'trcss=trcss.main:copy_css',  # Komut satırına trcss komutunu ekliyoruz
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)