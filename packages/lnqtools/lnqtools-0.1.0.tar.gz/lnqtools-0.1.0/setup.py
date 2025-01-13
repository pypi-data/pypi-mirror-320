from setuptools import setup, find_packages

setup(
    name='lnqtools',
    version='0.1.0',
    packages=find_packages(),
    description='A simple package for adding and multiplying numbers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='LyNgocQue',
    author_email='your_email@example.com',
    url='https://github.com/yourusername/your_project', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)