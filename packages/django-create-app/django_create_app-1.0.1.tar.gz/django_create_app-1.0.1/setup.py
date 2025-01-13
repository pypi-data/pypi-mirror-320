from setuptools import setup, find_packages

setup(
    name="django-create-app",
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="A Django app (custom) that modifies the startapp command to ensure all apps are created inside a directory defined by DEFAULT_APPS_DIR in settings.py.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sachin-acharya-projects/django-create-app",
    author="Sachin Acharya",
    keywords="django-create-app django-app django-startapp",
    install_requires=[
        "Django>=3.2",
    ],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)
# python .\setup.py sdist bdist_wheel