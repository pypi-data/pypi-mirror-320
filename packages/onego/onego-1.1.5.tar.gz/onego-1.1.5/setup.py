from setuptools import setup, find_packages

# with open('README.md', 'r', encoding='utf-8') as f:
#     readme = f.read()

VERSION = '1.1.5'

setup(
    name='onego',
    version=VERSION,
    description='Cool •-•',
    # long_description=readme,
    # long_description_content_type="text/markdown",
    license='Apache 2.0',
    author='th3poli',
    author_email='',
    keywords=['onego', 'all in one'],
    packages=find_packages(),
    # include_package_data=True,
    url='https://github.com/th3poli/onegopy',
    install_requires=[],
    extras_require={
        'sessions': ['cloudscraper', 'beautifulsoup4'],
        'files': [],
        'logger': [],
        'utils': ['requests', 'beautifulsoup4'],
        # 'chrome_driver': ['undetected-chromedriver'],
        'all': [
            'requests',
            'cloudscraper',
            'beautifulsoup4',
            # 'undetected-chromedriver'
        ],
    },
)

# OLD: python setup.py sdist bdist_wheel
# OLD: pip install ./dist/onego-1.0.0.tar.gz --no-cache-dir

# NEW: python -m build
# NEW: pip install ./dist/onego-1.1.0-py3-none-any.whl --no-cache-dir
# python -m twine upload .\dist\*

# import os;print('Local install command -> pip3 install ' + os.path.join(os.getcwd(), 'dist', f'onego-{VERSION}.tar.gz --no-cache-dir'))
# import os;print('Local install command -> pip3 install ' + os.path.join(os.getcwd(), 'dist', f'onego-{VERSION}-py3-none-any.whl --no-cache-dir'))