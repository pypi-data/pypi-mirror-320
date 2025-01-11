from setuptools import setup

setup(name='datupapi',
      version='1.101.6',
      description='Utility library to support Datup AI MLOps processes',
      long_description_content_type="text/markdown",
      long_description="foo bar baz",
      author='Datup AI',
      author_email='ramiro@datup.ai',
      packages=[
          'datupapi',
          'datupapi.transform',
          'datupapi.configure',
          'datupapi.extract',
          'datupapi.prepare',
          'datupapi.feateng',
          'datupapi.inventory',
          'datupapi.inventory.src.DailyUsage',
          'datupapi.inventory.src.Format',
          'datupapi.inventory.src.InventoryFunctions',
          'datupapi.inventory.src.ProcessForecast', 
          'datupapi.inventory.src.SuggestedForecast',          
          'datupapi.inventory.src.Transformation',
          'datupapi.inventory.conf',
          'datupapi.distribution',
          'datupapi.distribution.src.DistributionFunctions',
          'datupapi.distribution.src.Format',
          'datupapi.distribution.conf',
          'datupapi.training',
          'datupapi.evaluate',
          'datupapi.predict',
          'datupapi.utils'
          
      ],
      install_requires=[
          'beautifulsoup4>=4.9.3',
          'boto3>=1.16.54',
          'catboost>=1.0.4',
          'datetime>=4.3',
          'google-cloud-bigquery>=2.34.2',
          'google-cloud-storage>=2.1.0',
          'hdbcli>=2.17.22',
          'lxml>=4.9.2',
          'mysql-connector-python>=8.0.24',
          'openpyxl>=3.0.6',
          'pandas>=1.3.4',
          'pulp>=2.7.0',
          'pyarrow>=10.0.1',
          'pymssql>=2.2.7',
          'pymysql>=1.0.2',
          'pytest>=6.2.1',
          'python-dateutil>=2.8.2',
          'pyyaml>=5.3.1',
          'requests>=2.25.1',
          's3fs>=2023.6.0',
          'scikit-learn>=0.24.1',
          'shap>=0.40.0',
          'SQLAlchemy>=1.3.22',
          'sqlalchemy-hana>=0.5.0',
          'unidecode>=1.1.2',
          'xlrd>=1.0.0',
          'fuzzywuzzy>=0.18.0',
          'statsmodels>=0.13.2',
          'numpy>=1.21.6'
      ])
