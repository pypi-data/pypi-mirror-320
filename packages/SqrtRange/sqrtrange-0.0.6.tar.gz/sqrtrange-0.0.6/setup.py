from setuptools import setup, find_packages

setup(
    name='SqrtRange',         # Name of your package
    version='0.0.6',                  # Initial version
    description='SqrtRange is a python library used to generate Square root numbers in a range',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ricca665/SqrtRange',
    author='Ricca665',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.12',
    install_requires=[
        # Add dependencies here
    ],
)
