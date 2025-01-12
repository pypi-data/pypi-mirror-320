from setuptools import setup, find_packages

setup(
    name='anypayx',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'websocket-client',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'anypayx=anypayx.cli:cli',
        ],
    },
    author='Anypay',
    author_email='ops@anypayx.com',
    description='A CLI and library for Anypayx.com APIs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/anypayx/anypay-python',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
) 