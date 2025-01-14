from setuptools import setup, find_packages

setup(
    name='BioNet',
    version='0.1.0',
    description='A Python library for integrating biological network data with external service providers.',
    author='Brian Doyle',
    author_email='bdoyle@mitre.org',
    url='https://gitlab.com/groups/mitre-bionet', 
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
)
