from setuptools import setup, find_packages


def readme():
  with open('README.md', encoding='utf-8') as f:
    return f.read()


setup(
  name='scipystat',
  version='0.1.26',
  description='This is the simplest module for quick work with files.',
  license='MIT',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  package_data={
    'theory': ['*.png'],
  },
  install_requires=[
    'IPython','pyperclip'
  ],
)


