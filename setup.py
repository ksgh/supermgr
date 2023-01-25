from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

def get_version():
    #version_file = 'supermgr/_version.py'
    #exec (open(version_file).read())
    return '0.16'

setup(
    name='supermgr',
    version=get_version(),
    description='Easier Management of individual supervisord processes',
    long_description=readme(),
    url='https://github.com/ksgh/supermgr',
    author='Kyle Shenk',
    author_email='k.shenk@gmail.com',
    license='MIT',
    packages=['supermgr'],
    install_requires=[
        'colorama',
        'argparse',
        'tailer',
        'pylint'
    ],
    zip_safe=False,

    entry_points = {
        'console_scripts': ['supermgr=supermgr.cli:main'],
    }
)
