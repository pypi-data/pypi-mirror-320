from setuptools import setup, find_packages

setup(
    name="python-sandboxed-evaluator",
    version="0.1.0",
    author="Muhammad Haseeb",
    author_email="mhaseeb.inbox@gmail.com",
    description="A Python library for securely evaluating Python code in a sandboxed environment.",
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown",
    url="https://github.com/iam-mhaseeb/Python-Sandboxed-Evaluator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "RestrictedPython",
    ],
    test_suite="sandbox_evaluator_lib.tests",
    tests_require=["unittest"],
)
