# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slime_nlp']

package_data = \
{'': ['*']}

install_requires = \
['captum==0.7.0',
 'html2image==2.0.5',
 'ipython==8.12.3',
 'matplotlib==3.9.2',
 'numpy==2.1.2',
 'pandas==2.2.3',
 'scikit-learn==1.5.2',
 'seaborn>=0.13.2,<0.14.0',
 'setuptools>=75.6.0,<76.0.0',
 'statsmodels>=0.14.4,<0.15.0',
 'torch==2.3.0',
 'torcheval==0.0.7',
 'transformers==4.46.0']

setup_kwargs = {
    'name': 'slime-nlp',
    'version': '0.1.0',
    'description': 'SLIME - Statistical and Linguistic Insights for Model Explanation',
    'long_description': None,
    'author': 'Tibério Pereira',
    'author_email': 'tiberio@fisica.ufrn.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
