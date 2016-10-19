from setuptools import setup

setup(
    name='supermgr',
    version='0.1',
    description='Help manage supervisorctl',
    url='http://github.com/storborg/funniest',
    author='Kyle Shenk',
    author_email='k.shenk@gmail.com',
    license='MIT',
    packages=['supermgr'],
    install_requires=[
        'colorama',
    ],
    zip_safe=False,

    entry_points = {
        'console_scripts': ['supermgr=supermgr.cli:main'],
    }
)
