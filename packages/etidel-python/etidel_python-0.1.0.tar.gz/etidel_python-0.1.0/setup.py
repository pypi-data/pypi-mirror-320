from setuptools import setup, find_packages

setup(
    name="etidel_python",
    version="0.1.0",
    description="Un package Python pour envoyer des SMS via une API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="abdelkader etidel",
    author_email="a.etidel@l2t.io",
    url="https://github.com/votre_utilisateur/sms_sender",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.1",
    ],
)
