from setuptools import setup, Extension, find_packages

mymodule = Extension(
	'mymodule',
	sources=['mymodule.cp313-win_amd64.pyd']
)

setup(
	name='matkhau',
	version='0.1.0',
	description='A package with a compiled extension',
	ext_modules=[mymodule],
	author='Your Name',
	author_email='your_email@example.com',
	url='https://github.com/yourusername/your_project',
	packages=find_packages(),
	classifiers=[
		'Programming Language :: Python :: 3',
		'Operating System :: OS Independent',
	],
)