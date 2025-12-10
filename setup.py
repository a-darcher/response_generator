from setuptools import setup, find_packages

setup(
    name='response_stats',
    version='0.0.1',
    url='https://github.com/a-darcher/response_stats',
    author='Alana Darcher',
    author_email='darcher@tuta.io',
    description='response stats',
  #  install_requires=['numpy >= 1.11.1', 'matplotlib >= 1.5.1'],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)