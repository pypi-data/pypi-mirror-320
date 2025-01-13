from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()
f.close()

setup(
    name="kivy_file_manager_package",
    version="2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "kivy",
    ],
    description="Useful file manager app written in Kivy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'kivy_file_manager_package = kivy_file_manager_package.main:main'
        ]
    },
    package_data={
        '': ['kivy_file_manager_package/*'],
    },
)
