import os
from setuptools import setup, find_packages

VERSION = '0.0.19'
DESCRIPTION = 'eazyml image explain api'

# Setting up
setup(
    name="eazyml-xai-image",
    version=VERSION,
    author="Eazyml",
    author_email="admin@ipsoftlabs.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open("README.md", encoding="utf-8").read(),
    package_dir={"eazyml_xai_image":"./eazyml_xai_image"},
    # Includes additional non-Python files in the package.
    package_data={'' : ['*.py', '*.so', '*.dylib', '*.pyd']},
    install_requires=['tensorflow',
                      'segmentation-models==1.0.1',
                      'lime',
                      'opencv-python',
                      'flask',
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
