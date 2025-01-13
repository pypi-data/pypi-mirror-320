from setuptools import setup, find_packages

setup(
    name="customaaa",
    version="0.1.51",  # Incremented version
    author="Imtaiz",
    author_email="your.email@example.com",
    description="A toolkit for deploying various AI assistants to Hugging Face Spaces",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'streamlit>=1.31.0',
        'openai>=1.55.0',
        'python-dotenv>=1.0.0',
        'httpx>=0.26.0,<0.29.0',
        'huggingface_hub>=0.19.0',
        'supabase>=2.11.0',
        'dataclasses;python_version<"3.7"'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='ai, chatbot, huggingface, openai, streamlit, assistant',
)
