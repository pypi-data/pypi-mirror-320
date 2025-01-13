from setuptools import setup, find_packages

setup(
    name='PaleoSTeHM',                 # Package name based on your website/project
    version='1.0.0',                     # Initial version
    description='A modern, scalable Spatio-Temporal Hierarchical Modeling framework for paleo-environmental data',  # Brief description
    long_description=open('README.md').read(),  # Long description from README
    long_description_content_type='text/markdown',
    author='Yucheng Lin',                  # Replace with your name
    author_email='snqz1358@gmail.com',  # Replace with your email
    url='https://paleostehm.org/',       # Project website URL
    license='MIT',                       # License (change if necessary)
    packages=find_packages(),            # Automatically find packages
    install_requires=[
        'sphinx_copybutton',
        'sphinx-rtd-theme',
        'cartopy',
        'matplotlib',
        'numpy',
        'torch==2.3.1',
        'pandas==1.3.4',
        'scipy',
        'pyro-ppl',
        'tqdm==4.62.3',
        'seaborn==0.11.2',
        'statsmodels==0.14.0',
        'astropy',
        'openpyxl',
        'jupyter==1.0.0',
        'ipywidgets',
        'netcdf4==1.6.5',
        'ipykernel',
        'nmmn',
        'pip==21.2.4'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
    ],
    python_requires='>=3.7',             # Python version compatibility
    keywords='paleoenviromental, spatio-temporal, hierarchical modeling',  # Keywords for your project
    project_urls={                       # Additional project URLs
        'Homepage': 'https://paleostehm.org/',
        'Source': 'https://github.com/radical-collaboration/PaleoSTeHM',  # Update with your GitHub repo
        'Tracker': 'https://github.com/radical-collaboration/PaleoSTeHM/issues',  # Issue tracker
    },
)
