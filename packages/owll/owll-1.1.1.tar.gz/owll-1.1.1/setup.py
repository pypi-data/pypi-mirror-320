from setuptools import setup, find_packages

setup(
    name="owll",
    version="1.1.1",
    author="Jina",
    description="OWLL: AndroidManifest.xml Analyzer",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "colorama>=0.4.4",
	"lxml>=4.9.1",
    ],
    entry_points={
        "console_scripts": [
            "owll=owll.owll:main",
        ],
    },
)
