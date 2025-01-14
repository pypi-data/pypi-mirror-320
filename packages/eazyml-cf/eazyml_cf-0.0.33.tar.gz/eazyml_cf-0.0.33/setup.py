import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.33'
DESCRIPTION = 'Python client for Counterfactual'

# Setting up
setup(
    name="eazyml-cf",
    version=VERSION,
    author="Eazyml",
    author_email="admin@ipsoftlabs.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    package_dir={"eazyml_cf":"./eazyml_cf"},
    # Includes additional non-Python files in the package.
    package_data={'' : ['*.py', '*.so', '*.dylib', '*.pyd']},
    install_requires=['pandas',
                      'matplotlib',
                      'openpyxl',
                      'scikit-learn',
                      'scipy',
                      'getmac',
                      'cryptography',
                      'pyyaml'
                      ],
    keywords=['python'],
    python_requires=">=3.8",
    url="https://eazyml.com/",
    project_urls={
        "Documentation": "https://docs.eazyml.com/",
        "Homepage": "https://eazyml.com/",
        "Contact Us": "https://eazyml.com/trust-in-ai"
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        # "Development Status :: 5 - Production/Stable",
        "License :: Other/Proprietary License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ]
)
