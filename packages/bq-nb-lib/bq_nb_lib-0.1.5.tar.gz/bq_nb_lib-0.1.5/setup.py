from setuptools import setup, find_packages

setup(
    name="bq_nb_lib",
    version="0.1.5",
    description="A utility package for managing S3, Slack, and AlertOps integrations.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Rashed",
    author_email="Rashed@terdac.com",
    #url="https://github.com/yourusername/your_package_name",  # Optional
    packages=find_packages(),
    install_requires=[
        "requests",
        "google-cloud-secret-manager",
        "boto3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
