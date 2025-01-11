# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magnet_data',
 'magnet_data.currencies',
 'magnet_data.holidays',
 'magnet_data.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.2']

setup_kwargs = {
    'name': 'django-magnet-data',
    'version': '1.2.1',
    'description': 'An API client for data.magnet.cl',
    'long_description': '# django-magnet-data\nAn API client for data.magnet.cl\n\n![Django tests](https://github.com/magnet-cl/django-magnet-data/actions/workflows/django.yml/badge.svg)\n\n## Features\n\n-   Obtain values for multiple currencies in CLP\n\n## Requirements\n\n-   Django >=2.2\n-   Python >=3.6\n\n## Installation\n\n### Get the distribution\n\nInstall django-magnet-data with pip:\n```bash\n\n    pip install django-magnet-data\n```\n\n### Configuration\n\nAdd `magnet_data` to your `INSTALLED_APPS`:\n```bash\n    INSTALLED_APPS =(\n        ...\n        "magnet_data",\n        ...\n    )\n```\n\n## Currency API\n\nMagnet data handles the value of 4 currencies: `CLP`, `USD`, `EUR`, and `CLF`. Currently the api can only return the values of this currencies in `CLP`.\n\nValues are returned as [decimal.Decimal](https://docs.python.org/3/library/decimal.html "decimal.Decimal")\n\nTo get the value of a non  `CLP` currency for a given date in  `CLP`:\n\n``` python\nimport datetime\nfrom magnet_data.magnet_data_client import MagnetDataClient\n\nmagnet_data_client = MagnetDataClient()\ncurrencies = magnet_data_client.currencies\n\nclf_to_clp_converter = currencies.get_pair(currencies.CLF, currencies.CLP)\n# same as\nclf_to_clp_converter = currencies.get_pair(\n    base_currency=currencies.CLF, \n    counter_currency=currencies.CLP\n)\n\n# get the current value\nclf_in_clp = clf_to_clp_converter.now()\n\n# get the latest value\nlast_known_clf_in_clp = clf_to_clp_converter.latest()\n\n# get the value for a given date\ndate = datetime.date(2022, 7, 5)\nclf_in_clp_on_july_fifth = clf_to_clp_converter.on_date(date=date)\n\n# get a dict of values values for a month where the key is a datetime.date\nclf_in_clp_on_july = clf_to_clp_converter.on_month(2022, 7)\n```\n\n### choices for a django model\n\nIf you require a currency attribute in your models it can be done with\n`CurrencyAcronyms`:\n\n```\nfrom django.db import models\nfrom magnet_data.currencies.enums import CurrencyAcronyms\n\nclass MyModel(models.Model):\n    currency = models.CharField(\n        _("currency"),\n        max_length=5,\n        choices=CurrencyAcronyms.django_model_choices,\n    )\n\n```\n\n## Holidays API\n\nMagnet data handles Chilean holidays, but is built to handle other countries\n(is just that it does not store values for other countries).\n\nCountries are specified by country code taken from: [ISO 3166 country codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes).\n\nTo check if a date is a holiday in a given country:\n\n``` python\nimport datetime\nfrom magnet_data.magnet_data_client import MagnetDataClient\n\nmagnet_data_client = MagnetDataClient()\nholidays = magnet_data_client.holidays\nholidays.is_workday(datetime.date(2023, 1, 2), holidays.CL)  # False\nholidays.is_workday(datetime.date(2023, 1, 3), holidays.CL)  # True\n\n# get the next date that will be a business day. This returns datetime.date(2023, 1, 3)\nholidays.get_next_business_day(\n    country_code=holidays.CL,\n    from_date=datetime.date(2022, 12, 31),\n)\n\nbusiness_days_count -- number of business days to count (default 1)\n# This returns datetime.date(2023, 1, 5)\nholidays.get_next_business_day(\n    country_code=holidays.CL,\n    from_date=datetime.date(2022, 12, 31),\n    business_days_count=3,\n)\n\n# step -- the amount by which the index increases. (default 1)\n# This returns datetime.date(2023, 1, 3)\nholidays.get_next_business_day(\n    country_code=holidays.CL,\n    from_date=datetime.date(2022, 12, 31),\n    step=3,\n)\n\n# And this returns datetime.date(2023, 1, 4)\nholidays.get_next_business_day(\n    country_code=holidays.CL,\n    from_date=datetime.date(2023, 1, 1),\n    step=3,\n)\n\n# get the number of holidays wasted on weekdays. This example returns 1\nholidays.get_holidays_count_during_weekdays(\n    holidays.CL,\n    datetime.date(2022, 12, 30),\n    datetime.date(2023, 1, 7),\n)\n```\n\n## Contribute\n\n### Local development\n\nTo develop locally, install requirements using\n[poetry](https://python-poetry.org/).\n\n```bash\n\n    poetry install\n```\n\n### Testing\n\nTest are written using the django testing framework: https://docs.djangoproject.com/en/4.1/topics/testing/\n\nAll tests are stored in the `tests` folder.\n\nAll new features have to be tested.\n[poetry](https://python-poetry.org/).\n\n```bash\n\n    python manage.py test\n```\n\n\n### New features\n\nTo develop new features, create a pull request, specifying what you are\nfixing / adding and the issue it\'s addressing if there is one.\n\nAll new features need a test in the `tests` folder.\n\nAll tests need to pass in order for a maintainer to merge the pull request.\n\n\n### Publish\n\nUse poetry to publish. You\'ll need a pypi token to publish in the project\nroot.\n\nOn the project root, run:\n\n```bash\n\n    poetry build\n    poetry publish\n```\n',
    'author': 'Ignacio Munizaga',
    'author_email': 'muni@magnet.cl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/magnet-cl/django-magnet-data',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
