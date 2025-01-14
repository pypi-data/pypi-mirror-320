from setuptools import setup, find_packages

setup(
    name='cipherbyte',
    version='0.1.4',  # Версия
    py_modules=["cipherbyte"],
    packages=find_packages(),
    author='Kiyatsuka',
    author_email='saglotuspetrovih33@gmail.com',
    description='Decrypt python data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/walidname113',
    license='MIT',
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
