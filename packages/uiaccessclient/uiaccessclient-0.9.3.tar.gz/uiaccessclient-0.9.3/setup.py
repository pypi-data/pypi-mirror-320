from setuptools import setup, find_packages

setup(
    name="uiaccessclient",
    version="0.9.3",
    description="UniFi Access API",
    keywords=["UniFi Access API"],
    install_requires=[
        "aiohttp >= 3.11.11, < 4.0.0",
        "urllib3 >= 1.25.3, < 3.0.0",
        "python_dateutil >= 2.8.2",
        "pydantic >= 2",
        "typing-extensions >= 4.7.1",
    ],
    packages=find_packages(),
    include_package_data=True,
    project_urls={
        "Source": "https://github.com/hagen93/uiaccessclient",
        "Documentation": "https://core-config-gfoz.uid.alpha.ui.com/configs/unifi-access/api_reference.pdf",
    },
)
