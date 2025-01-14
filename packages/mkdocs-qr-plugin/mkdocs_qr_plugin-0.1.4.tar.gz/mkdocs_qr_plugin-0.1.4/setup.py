from setuptools import setup, find_packages

setup(
    name='mkdocs_qr_plugin',
    version='0.1.4',
    description='An MkDocs plugin for generating QR codes',
    long_description='An MkDocs plugin that automagically generates qr codes',
    keywords='mkdocs',
    url= 'https://github.com/miguelhatricks/mkdocs-qr-plugin',
    author='Miguel Hatrick',
    author_email='miguel@dacosys.com',
    license='MIT',
    python_requires='>=3.6',
    install_requires=[
        'mkdocs>=1.5',
        'qrcode==8.0',
    ],
    extras_require={
        'dev': [ 'pytest']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'qr = mkdocs_qr_plugin.plugin:QRPlugin',
        ]
    }
)
