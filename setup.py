from setuptools import setup, find_packages

setup(
    name="eiai_kcaf",
    description="EIAI Kubernetes Cluster Automation Framework",
    version="0.0.3",
    author="Eiai365 Eiai",
    author_email="eiai365.eiai@gmail.com",
    install_requires=[
        'slack-sdk',
        'ratelimit',
        'backoff',
    ],
    packages=find_packages(),
)
