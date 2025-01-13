from setuptools import setup, find_packages

setup(
    name="helix-agent",
    version="1.2.0",
    description="A Python package for creating science-themed AI agents with research and experimentation capabilities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Helix Agent",
    author_email="helixagentsol@gmail.com",
    url="https://github.com/helixagent/helix-agent",
    packages=find_packages(),
    install_requires=[
        "openai>=0.28.0",
        "asyncio",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "tweepy>=4.12.0",
        "python-dateutil>=2.8.2",
        # ML Tools dependencies
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "plotly>=5.3.0",
        # Research Tools dependencies
        "PyPDF2>=3.0.0",
        "arxiv>=1.4.0",
        "networkx>=2.6.0",
        # Data Tools dependencies
        "pyyaml>=6.0.0",
        # Collaboration Tools dependencies
        "gitpython>=3.1.0",
        "nbformat>=5.7.0",
        "markdown2>=2.4.0",
        "jupyter>=1.0.0"
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'flake8>=4.0.0',
        ],
        'ml': [
            'torch>=1.9.0',
            'tensorflow>=2.6.0',
            'xgboost>=1.5.0',
            'lightgbm>=3.3.0'
        ],
        'viz': [
            'bokeh>=2.4.0',
            'altair>=4.2.0',
            'plotly-express>=0.4.0'
        ],
        'nlp': [
            'nltk>=3.6.0',
            'spacy>=3.2.0',
            'gensim>=4.1.0'
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="AI, OpenAI, science, research, agents, GPT, Helix, DeSci, experiments, analysis, machine learning, data science, collaboration",
    license="MIT",
    project_urls={
        "Documentation": "https://github.com/helixagent/helix-agent/tree/main/docs",
        "Source": "https://github.com/helixagent/helix-agent",
        "Issues": "https://github.com/helixagent/helix-agent/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
