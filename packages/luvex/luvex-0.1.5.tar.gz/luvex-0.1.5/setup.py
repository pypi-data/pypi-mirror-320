from setuptools import setup, find_packages

setup(
    name='luvex',
    version='0.1.5',
    packages=find_packages(),
    install_requires=[
        'numpy','scikit-learn'
    ],
    author='Gladson K',
    author_email='gladson1414@gmail.com',
    description='Regression - Linear(Least Squares Method), Multiple Linear . Classification - KNN, Logistic Regression, Decision Trees, Random Forests ',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Gladson-K/luvex',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)