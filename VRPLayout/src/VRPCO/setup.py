from setuptools import find_packages, setup

long_description = '''
                    QIntern 2021
Implementation of space-efficient variational algorithms 
for the Graph Coloring or Traveling Salesperson problems 
in Qiskit 
Classical Optimisation module
'''

setup(
    name="VRPCO",
    version="0.0.1",
    description="A Classical Optimisation Toolkit for the Vehicle Routing Problem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/qworld/qresearch/qintern2021/21_solving-vehicle-routing-problem-and-its-variants-using-quantum-computing_b",
    project_urls={
        "HomePage": "https://qworld.net/",
    },
    keywords='vrp quantum classical optimisation',
    packages=find_packages(),
    install_requires=[
        "matplotlib==3.5.1", 
        "cplex",
        "pygsp",
        "networkx",
        "dwave-ocean-sdk",
        "pandas",
        "pulp",
        "pytest"
    ],
    classifiers=[
        # Project Maturity
        "Development Status :: 1 - Planning",

        # Topic
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Physics",

        # Intended Audience
        "Intended Audience :: Science/Research",

        # Compatibility
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",

        # Python Version
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
)