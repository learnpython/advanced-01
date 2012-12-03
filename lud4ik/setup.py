from distutils.core import setup


setup(name='socket start',
      version='0.1',
      description='Socket server and client for very simple protocol.',
      author='Ludmila Lukashevskaya',
      author_email='lukashe@ukr.net',
      url='https://github.com/lud4ik/advanced-01.git',
      classifiers=[
        'Programming Language :: Python :: 3.3',        
        ],
      packages=['work'],
      py_modules = ['command_client', 'command_server'],
    )