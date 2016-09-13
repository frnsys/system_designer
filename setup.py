from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='syd',
    version='0.0.1',
    description='a distributed agent-based simulation framework',
    url='https://github.com/frnsys/system_designer',
    author='Francis Tseng (@frnsys)',
    author_email='f@frnsys.com',
    license='MIT',
    packages=find_packages(),
    install_requires=required,
    test_requires=['nose'],
    test_suite='nose.collector',
    entry_points='''
        [console_scripts]
        syd=syd.cli:cli
    '''
)