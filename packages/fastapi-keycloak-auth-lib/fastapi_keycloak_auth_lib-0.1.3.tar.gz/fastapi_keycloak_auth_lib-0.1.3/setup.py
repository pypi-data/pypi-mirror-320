from setuptools import setup, find_packages

setup(
    name="fastapi-keycloak-auth-lib",
    version="0.1.3",
    description="FastAPI integration with Keycloak for authentication and role-based access control",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="shareef",
    author_email="your.email@example.com",
    url="https://github.com/your-username/fastapi-keycloak-auth",
    packages=find_packages(),
    install_requires=[
        "requests",
        "fastapi",
        "cryptography",
        "authlib",
        "python-dotenv",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
