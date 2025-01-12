from setuptools import setup

setup(
    name="QuakeAgent",
    version="0.1.0",
    long_description="QuakeAgent",
    long_description_content_type="text/markdown",
    packages=["quakeagent"],
    install_requires=["numpy",  "h5py", "matplotlib", "pandas"],
)
