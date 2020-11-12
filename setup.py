from setuptools import setup, find_packages

LONG_DESCRIPTION = open("README.md").read()

INSTALL_REQUIRES = [
    "boto==2.49.0",
    "Click==7.0",
]

setup(
    name="aws-service-roles-manager",
    url="http://github.com/servian/aws-service-roles/",
    author="Marat Levit",
    author_email="marat.levit@servian.com",
    version="0.1",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("src"),
    description="A command-line tool for creating and deleting IAM Roles for each AWS service",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    py_modules=["aws-service-roles-manager"],
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "aws-service-roles-manager=aws_service_roles_manager.cli:main"
        ]
    },
)