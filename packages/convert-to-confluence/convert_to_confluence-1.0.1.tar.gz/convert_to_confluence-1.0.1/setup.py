from setuptools import setup, find_packages

setup(
    name='convert_to_confluence',
    version='1.0.1',
    description='A Python package to convert Markdown to Confluence format.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Aryaman Gurjar',
    author_email='aryamangurjar6@gmail.com',
    url='https://github.com/AryamanGurjar/Confluence-Wiki-Formatter-Package',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
