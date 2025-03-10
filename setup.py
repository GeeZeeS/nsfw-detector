from setuptools import setup, find_packages

setup(
    name="nsfw-detector",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "python-magic>=0.4.24",
        "Pillow>=8.3.1",
        "python-docx>=0.8.11",
        "python-doc>=0.1.0",
        "PyPDF2>=2.0.0",
        "opencv-python>=4.5.3",
        "numpy>=1.21.2",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "pdf2image>=1.16.3",
        "rarfile>=4.0",
        "python-magic-bin>=0.4.14; platform_system=='Windows'",
    ],
    entry_points={
        "forge.plugins": [
            "nsfw_detector=nsfw_detector:register"
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="NSFW content detection plugin for Forge UI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nsfw-detector",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    zip_safe=False,
) 