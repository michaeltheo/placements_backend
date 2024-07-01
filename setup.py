from setuptools import setup, find_packages


def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="placements_api",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.7',
    author="Michael Theocharis",
    author_email="michaeltheochar@gmail.com",
    description="IHU Placements API",
    url="https://github.com/michaeltheo/placements_backend",
)
