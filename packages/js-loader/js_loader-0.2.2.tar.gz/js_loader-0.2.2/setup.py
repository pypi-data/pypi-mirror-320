from pathlib import Path
  
import setuptools
  
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="js-loader",
    version="0.2.2",
    author="Hans Then",
    author_email="hans.then@gmail.com",
    description="Load javascript files as python modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    extra_requires={
        "pythonmonkey": ["pythonmonkey"],
    }
)

