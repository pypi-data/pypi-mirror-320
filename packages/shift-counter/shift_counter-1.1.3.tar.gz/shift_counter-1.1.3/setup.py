from setuptools import setup, find_packages

setup(
    name='shift_counter',
    version='1.1.3',
    author='Daniel Simanek',
    author_email='daniel.simanek@decathlon.com',
    description='Library for processing attendance plan data into time-segmented DataFrames',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/daniel-simanek/shift-counter',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.7',
)