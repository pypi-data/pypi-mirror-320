from distutils.core import setup
from setuptools import find_packages
setup(
  name = 'CogentDataHubAPI',          
  version = '0.1.1',      
  license='MIT',        
  description = 'Python API for real-time data access to Cogent DataHub',   
  author = 'Colin Yuen',                   
  author_email = 'colin.yuen@skkynet.com',      
  url = 'https://github.com/cogentrts/DataHubPythonAPI',   
  download_url = 'https://github.com/cogentrts/DataHubPythonAPI/archive/refs/tags/v0.1.1.tar.gz',    
  keywords = ['Cogent', 'DataHub', 'Api', 'Python'],   
  packages=find_packages(),
  install_requires=[           
        'matplotlib>=3.0.0',  
        'dataclasses; python_version < "3.7"'  
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
  ],
)