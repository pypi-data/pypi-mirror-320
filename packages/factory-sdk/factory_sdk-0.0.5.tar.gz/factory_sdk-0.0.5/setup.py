from setuptools import setup, find_packages

# Read the contents of your README file (optional)
def readme():
    try:
        with open('README.md', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ''

# Read the contents of your requirements.txt file
def parse_requirements():
    try:
        with open('requirements.txt', encoding='utf-8') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []
    
from setuptools.command.install import install
import subprocess
import sys
class InstallWithNuitka(install):
    """Custom install command that runs Nuitka compilation after normal install."""
    def run(self):
        # First, run the standard install
        super().run()

        # Then attempt to compile with Nuitka
        try:
            subprocess.check_call([
                sys.executable, 
                '-m', 'nuitka', 
                '--module', 
                'factory_sdk'  # or the actual folder/entrypoint you want compiled
            ])
            print("Successfully compiled factory-sdk with Nuitka.")
        except Exception as e:
            print("Nuitka compilation failed:", e)

setup(
    name='factory-sdk',  # The name of your package on PyPI
    version='0.0.5',  # Start with a semantic version, e.g., major.minor.patch
    description='A Python SDK for interfacing with the Factory API',
    long_description=readme(),
    long_description_content_type='text/markdown',  # README file format (Markdown)
    author='manufactAI',  # Your name
    author_email='dev@manufactai.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='sdk factory api integration',  # Keywords for your package
    packages=find_packages(),  # Automatically find and include all packages in your project
    python_requires='>=3.7',  # Minimum Python version required
    install_requires=parse_requirements(),  # Dependencies for your package

    include_package_data=False,  # Include files specified in MANIFEST.in
    project_urls={  # Additional URLs for the project
        
    },
    cmdclass={
        'install': InstallWithNuitka,
    },
)
