from setuptools import setup, find_packages

setup(
    name="db_helper_lib",  
    version="0.2.0",  
    description="Библиотека позволяет быстро выполнять запросы к БД, а также превращать данные в JSON",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown', 
    author="LostKosmonaut", 
    author_email="maxon1204@gmail.com",  
    url="https://github.com/LostKosmonaut26/db_helper",  
    packages=find_packages(),  
    install_requires=[  
        "pyodbc",  
    ],
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  
)
