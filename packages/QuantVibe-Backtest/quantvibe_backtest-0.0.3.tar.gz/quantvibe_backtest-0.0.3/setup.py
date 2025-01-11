from setuptools import setup, find_packages

setup(
    name="QuantVibe_Backtest",  # Unique name for your package
    version="0.0.3",    # Initial version
    author="Fang Kai Hock",
    author_email="fkh714@gmail.com",
    description="Python package for internal backtest",
    include_package_data=False,
    install_requires=[
    "matplotlib",  # For plotting with pyplot and other functions
    "seaborn",     # For statistical data visualization
    "pandas",      # For data manipulation and analysis
    "numpy",       # For numerical computing
    ],
)
