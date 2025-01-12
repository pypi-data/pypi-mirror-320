from setuptools import setup, find_packages

setup(
    name='SimpSave',
    version='0.1.1',
    packages=find_packages(where='source'),
    include_package_data=True,
    install_requires=[],
    author='WaterRun',
    author_email='2263633954@qq.com',
    description='SimpSave: Easy Python Basic Variable Persistence Library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Water-Run/SimpSave',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
