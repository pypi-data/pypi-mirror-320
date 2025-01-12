import setuptools

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

packages = setuptools.find_packages(where='.', exclude=['tests', 'tests.*'])
print("Found packages:", packages)

setuptools.setup(
    name='QCo',
    version='0.9.5.4',
    url='https://pypi.org/manage/account/token/',
    packages=setuptools.find_packages(where='.', exclude=['tests', 'tests.*']),
    license='',
    author='FF',
    author_email='',
    description='',
    install_requires=[
        'protobuf',
        'cryptography',
        'bs4',
        'urllib3==1.26.16',
        'pydantic',
        'requests',
        'python-box',
        'PySocks',
        'python-box',
        'loguru'
    ]

)
