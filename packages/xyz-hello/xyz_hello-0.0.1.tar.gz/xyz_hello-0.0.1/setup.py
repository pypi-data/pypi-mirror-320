from setuptools import setup , find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xyz_hello",
    version=0.3,
    package = find_packages(),
    install_requires=[
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",  # Explicitly specify Markdown

    entry_points={
        "console_scripts":[
                "say_hello=xyz_hello:Hello",
        ]
    }
)



# [project.urls]
# Homepage = "https://github.com/pypa/sampleproject"
# Issues = "https://github.com/pypa/sampleproject/issues"