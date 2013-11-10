from setuptools import setup, find_packages

setup(
        name = 'tarifcalc',
        version = '0.2',
        packages = find_packages(),
        install_requires = ['dbf>=0.95'],

        author = 'TemaPut',
        author_email = 'putilkin@gmail.com',
        description = "Estimate delivery charges by Russian post",
        keywords = "russian post tarif delivery",
        url = "http://github.com/temaput/tarifcalc2"
        )
