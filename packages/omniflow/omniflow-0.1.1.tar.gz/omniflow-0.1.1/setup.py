from setuptools import setup, find_packages

setup(
    name='omniflow',
    version='0.1.1',
    author='James Brogan',  # Replace with your name
    author_email='james.brogan@vumc.org',  # Replace with your email
    description='OMOP CDM data harmonization and quality control tool',  # Replace with your package description
    long_description=open('README.md').read(),  # Assuming you have a README.md file
    long_description_content_type='text/markdown',
    url='https://github.com/bicklab/omniflow',  # Replace with your project's URL
    packages=find_packages(),
    install_requires=[
        'polars',
        'pyarrow',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',  # Replace with your license if different
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
