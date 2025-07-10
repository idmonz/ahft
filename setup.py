from setuptools import setup, find_packages
setup(
    name="tvscript_tester",
    version="0.4.3",
    packages=find_packages(),
    entry_points={"console_scripts": ["tvscript-tester=tvscript_tester.cli:main"]},
)
