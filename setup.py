from setuptools import setup, find_packages

version = '0.0.4'

install_requires = [
    "SQLAlchemy",
    "pysqlite",
    "colorama",
    "pyfiglet",
    "python-dateutil",
    "termcolor",
    "twitter",
    "Pillow",
    "requests",
]

setup(name='rainbowstream',
      version=version,
      description="A colorful terminal-based Twitter client. Streaming API supportd.",
      long_description=open("./README.rst", "r").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
      ],
      keywords='twitter, command-line tools, web 2.0, stream API',
      author='Vu Nhat Minh',
      author_email='nhatminh_179@hotmail.com',
      url='https://github.com/DTVD/rainbowstream',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      rainbow=rainbowstream.rainbow:fly
      """,
      )
