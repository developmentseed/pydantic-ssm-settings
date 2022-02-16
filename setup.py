from setuptools import find_namespace_packages, setup

with open("README.md") as f:
    desc = f.read()

setup(
    name="pydantic-ssm-settings",
    description="A Pydantic configuration provider for AWS SSM Parameter Store.",
    long_description=desc,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="Pydantic AWS SSM Parameter Store",
    author=u"Anthony Lukach",
    author_email="anthony@developmentseed.org",
    url="https://github.com/developmentseed/pydantic-ssm-settings",
    license="MIT",
    packages=find_namespace_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=[
        "pydantic",
    ],
    extras_require={"cli": ["boto3", "click", "python-dotenv"]},
    entry_points={
        "console_scripts": [
            "dotenv-to-ssm = dotenv_to_ssm:load [cli]",
        ]
    },
)
