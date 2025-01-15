from setuptools import setup, find_packages
import os 

with open(os.path.join("JVLMotor", "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="JVLMotor",  # Replace with your package name
    version="0.0.4",        # Define your version
    packages=find_packages(),  # Automatically find and include all packages
    install_requires=["ea_psu_controller==1.1.0",
                        "libscrc==1.8.1",
                        "pymodbus==3.5.2",
                        "pyserial==3.5",
                        "pyuac==0.0.3",
                        "pywinauto==0.6.8"],    # List any dependencies here
    include_package_data=True,  # Include files from MANIFEST.in
    author="JVL A/S",
    author_email="atv@jvl.dk",
    maintainer='JVL A/S',
    maintainer_email='Support@jvl.dk',
    description="A library for JVL motors communication with different protocols",
    long_description=long_description,
    long_description_content_type="text/markdown", 
    license="MIT",  # Specify a license, e.g., MIT
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9.4"
    #url="https://example.com",  # Replace with your project URL
)
