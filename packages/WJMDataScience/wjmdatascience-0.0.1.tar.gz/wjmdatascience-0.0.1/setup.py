from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: MacOS :: MacOS X',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3.13'
]
 
setup(
  name='WJMDataScience',
  version='0.0.1',
  description='A very basic data cleaning and preprocessing library',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Will McCarter',
  author_email='wjmmccart@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='data analysis cleaning preprocessing',
  packages=find_packages(),
  install_requires = ['pandas', 'numpy', 'scikit-learn'],
  )