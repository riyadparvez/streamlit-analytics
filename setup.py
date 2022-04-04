import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = ['streamlit_analytics']

requires = [
    'loguru',
    'pandas',
    'streamlit',
    'sqlalchemy',
    'sqlmodel',
]

setuptools.setup(
    name="streamlit-analytics",
    version="0.0.1",
    author="Riyad Parvez",
    author_email="riyad.parvez@gmail.com",
    description="Streamlit Analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riyadparvez/streamlit-analytics",
    # packages=setuptools.find_packages(),
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Proprietary",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=requires
)
