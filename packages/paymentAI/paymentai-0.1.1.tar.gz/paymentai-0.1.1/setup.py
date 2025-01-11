from setuptools import setup, find_packages

setup(
    name="paymentAI",
    version="0.1.1",
    author="paymentAI",
    author_email="janaka@agentpaid.ai",
    description="A package to handle transaction events and send payloads.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AgentPaid/ap-client",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
