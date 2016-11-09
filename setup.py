from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='supermgr',
    version='0.7',
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
        'tailer'
    ],
    zip_safe=False,

    entry_points = {
        'console_scripts': ['supermgr=supermgr.cli:main'],
    }
)
