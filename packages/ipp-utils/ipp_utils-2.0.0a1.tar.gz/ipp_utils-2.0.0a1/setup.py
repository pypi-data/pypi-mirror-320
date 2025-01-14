from setuptools import find_packages, setup
from ipp_utils import __version__

setup(
    name="ipp_utils",
    version=__version__,
    description="Utils for Intel® Integrated Performance Primitives",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='veennn',
    author_email='veennn@proton.com',
    url="",
    python_requires='>=3.8.0',
    # packages=find_packages(),
    packages=['ipp_utils'],
    # ext_package=['ipp_utils.__pycache__'],
    package_data={'ipp_utils': ['normalize_rfft.so', 'normalize_rfft.dll', '_ipp_utils.py', '__init__.py']},
    install_requires=['scipy', 'ipp-devel', 'ipp', 'ipp-include'],
    keywords='''''',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
    ],
)
