from setuptools import setup

setup(
    name='supermgr',
    version='0.1',
    description='Easier Management of individual supervisord processes',
    url='https://github.com/ksgh/supermgr',
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
