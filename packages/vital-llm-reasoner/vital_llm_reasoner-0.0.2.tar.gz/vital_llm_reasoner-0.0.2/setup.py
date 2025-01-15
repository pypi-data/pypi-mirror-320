from setuptools import setup, find_packages

setup(
    name='vital-llm-reasoner',
    version='0.0.2',
    author='Marc Hadfield',
    author_email='marc@vital.ai',
    description='Vital LLM Reasoner',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vital-ai/vital-llm-reasoner',
    packages=find_packages(exclude=["test", "test_data"]),
    license='Apache License 2.0',
    install_requires=[

            'numpy>=1.21.0',
            'torch',
            'transformers',
            'sentencepiece',
            'tqdm',
            'nltk',
            'bs4',
            'pdfplumber',
            'pyppeteer',

            'vital-logic>=0.1.0',

            'vital-ai-vitalsigns>=0.1.27',
            'vital-ai-domain>=0.1.4',
            'pyyaml',
            'vital-ai-haley-kg>=0.1.24',
            'kgraphservice>=0.0.6',

            # 'pandas>=2.2.3',
            # 'scikit-learn>=1.6.0',

            'sentence_transformers>=3.3.1',

    ],
    extras_require={
        "llamacpp": [
            'llama-cpp-python>=0.2.20',
        ],
        "vllm": [
            'vllm>=0.6.6',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
