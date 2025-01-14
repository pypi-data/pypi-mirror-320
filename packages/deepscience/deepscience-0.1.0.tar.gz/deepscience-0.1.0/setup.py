from setuptools import setup, find_packages

setup(
    name='deepscience',
    version='0.1.0',
    description='An AI4S model toolkit',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='sugon-ai4s',
    author_email='lidong6@sugon.com',
    url='https://github.com/lzxdn/deepscience',  # or your project URL
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
