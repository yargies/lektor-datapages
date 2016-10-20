from setuptools import setup

setup(
    name='lektor-data-pages',
    version='0.1',
    author=u'Kenji Wellman',
    author_email='kenji.wellman@yargies.com',
    url='https://github.com/yargies/lektor-datapages', 
    license='MIT',
    py_modules=['lektor_data_pages'],
    entry_points={
        'lektor.plugins': [
            'data-pages = lektor_data_pages:DataPagesPlugin',
        ]
    }
)
