# setup.py

from setuptools import setup, find_packages

with open("pipme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mailship",
    version="1.0.3",
    author="Oluwaseyi Ajadi",
    author_email="oluwaseyinexus137@gmail.com",
    description="Mail Ship: A powerful Python library for email automation and testing. It offers Gmail integration, real-time inbox monitoring, content extraction, and seamless Selenium integration. Perfect for developers navigating complex email-based workflows and testing scenarios.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlazinArtemis/mail_ship/",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "beautifulsoup4",
        "google-auth",
        "cryptography",
        "pyvirtualdisplay>=3.0",
        "chromedriver-autoinstaller>=0.5",
        "selenium>=4.0.0"

    ],
    entry_points={
        "console_scripts": [
            "mail-ship-setup=mailship.setup_auth:main",
        ],
    }
)
