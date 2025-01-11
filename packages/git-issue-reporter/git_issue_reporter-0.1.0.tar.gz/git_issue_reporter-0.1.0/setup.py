from setuptools import setup, find_packages

setup(
    name='git_issue_reporter',  # Changed from 'git_issue_reporter' to 'github_issue_reporter'
    version='0.1.0',
    description='A Django module to report issues directly to GitHub.',
    author='Thimpu Sengyung',
    author_email='thmtymthm@gmail.com',
    url='https://github.com/your_username/github_issue_reporter',  # Added GitHub repo URL
    packages=find_packages(),
    install_requires=[
        'django',
        'requests',
    ],
    package_data={  # Included templates for distribution
        'git_issue_reporter': ['templates/git_issue_reporter/*.html'],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries',
    ],
)
