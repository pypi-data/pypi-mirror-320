from setuptools import setup, find_packages

requirements = open('requirements.txt').read().splitlines()
setup(
    name='srst-ordbok',
    version='0.1.0',
    #py_modules=['harken'],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        #'harken': ['assets/*'],
        'ordbok': [
            'static/css/*',
            'static/html/*',
            'static/js/*',
            'static/ordbok.png'
        ]
    },
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            # This allows you to create command-line tools.
            # Replace `your_script` with the name of the script users should run,
            # and `your_package.module:function` with the actual callable you want to run.
            # Example:
            # 'your_script = your_package.module:function',
            'srst-ordbok=ordbok.ordbok:main'
        ],
    },
    author='Yuri Bochkarev',
    author_email='baltazar.bz@gmail.com',
    description='A good mix of Norwegian dictionaries',
    long_description='', #open('README.md').read(),
    long_description_content_type='text/markdown',  # Requires setuptools>=38.6.0
    url='https://github.com/balta2ar/srst-ordbok',
    classifiers=[
        # Classifiers help users find your project. Full list:
        # https://pypi.org/classifiers/
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify the minimum Python version required
)
