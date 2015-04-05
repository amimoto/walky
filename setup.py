from setuptools import setup

setup(name='walky',
      version='0.1',
      description='Multi-Language Distributed Object Protcol',
      url='',
      author='Aki Mimoto',
      author_email='amimoto+walky@gmail.com',
      license='MIT',
      packages=['walky'],
      install_requires=[
          'tzlocal',
          'tornado',
          'python-dateutil',
      ],
      zip_safe=False)

