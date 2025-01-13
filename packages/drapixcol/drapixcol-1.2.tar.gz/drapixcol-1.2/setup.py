from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='drapixcol',
  version='1.2',
  author='Lina_Torovoltas',
  description='Python library for drawing with pixels.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/lina-torovoltas/Drapixcol',
  packages=find_packages(),
  install_requires=[
    'requests>=2.25.1',
    'pillow>=10.1.0',
    'opencv-python>=4.8.1.78',
    'numpy>=1.26.2'],
  classifiers=[
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='python color colors paint drapixcol pixel drawing',
  python_requires='>=3.9'
)
