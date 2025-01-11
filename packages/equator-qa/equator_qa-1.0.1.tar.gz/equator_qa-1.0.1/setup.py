from setuptools import setup, find_packages

setup(
    name='equator-qa',
    version='1.0.1',
    author='Ray Bernard',
    author_email='ray.bernard@outlook.com',
    description="Equator: A Deterministic Framework for Evaluating LLM Reasoning with Open-Ended Questions.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/raybernard/equator-qa',  # Replace with your actual GitHub repository URL
    packages=find_packages(include=["equator", "equator.*"]),
    include_package_data=False,  # No non-code files are included
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.18.0',
        'requests>=2.25.0',
        'jupyter',
    ],
    entry_points={
        "console_scripts": [
            "equator=equator.main:main",  # Entry point for CLI
        ],
    },
    keywords="LLM evaluation, open-ended questions, reasoning framework",
    license="MIT",
    extras_require={
        "dev": ["pytest", "flake8"],
    },
)
