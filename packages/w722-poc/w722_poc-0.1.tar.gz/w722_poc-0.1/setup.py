from setuptools import setup, find_packages

setup(
    name='w722-poc',
    version='0.1',
    packages=find_packages(),
    description='A Python package that executes a curl command upon installation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/w7_poc',  # Update with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
