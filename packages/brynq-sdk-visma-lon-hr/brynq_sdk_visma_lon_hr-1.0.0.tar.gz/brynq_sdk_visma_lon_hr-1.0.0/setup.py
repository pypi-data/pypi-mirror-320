from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_visma_lon_hr',
    version='1.0.0',
    description='Visma Lon & HR wrapper from BrynQ',
    long_description='Visma Lon & HR wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=2',
        'pandas>=2,<3'
    ],
    zip_safe=False,
)
