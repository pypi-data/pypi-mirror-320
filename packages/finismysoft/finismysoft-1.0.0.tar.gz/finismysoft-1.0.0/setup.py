from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

NAME="finismysoft"
VERSION="1.0.0"
DESCRIPTION="MySoft E Fatura API için Python istemcisi"
AUTHOR="Hasan Çağrı Güngör"
AUTHOR_EMAIL="iletisim@cagrigungor.com"
LICENSE="MIT"
KEYWORDS="mysoft,finis,çağrı güngör,e-fatura,e-arşiv,e-irsaliye,e-defter"

setup(
    name="finismysoft",
    version="1.0.0",
    description="MySoft E Fatura API için Python istemcisi",
    author="Hasan Çağrı Güngör",
    author_email="iletisim@cagrigungor.com",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    python_requires=">=3.6",
    license="MIT",
    keywords="mysoft,finis,çağrı güngör,e-fatura,e-arşiv,e-irsaliye,e-defter",
    py_modules=["finismysoft"],
)
