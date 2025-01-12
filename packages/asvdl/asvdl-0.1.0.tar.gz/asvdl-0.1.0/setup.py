from setuptools import setup, find_packages

setup(
    name='asvdl',  # Name of the package
    version='0.1.0',   # Version number
    packages=find_packages(),  # Automatically finds the package directory
    include_package_data=True,  # Include additional files specified in MANIFEST.in
    long_description=open('README.md').read(),  # Read long description from README.md
    long_description_content_type='text/markdown',  # Format of long description
    author='Your Name',
    author_email='your.email@example.com',
    description='A package that includes .txt files with Python programs.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
