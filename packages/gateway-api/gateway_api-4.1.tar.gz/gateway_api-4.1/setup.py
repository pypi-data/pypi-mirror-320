from setuptools import setup

setup(name='gateway_api',
      version='4.1',
      description='Gateway API Pulls and Requests',
      author='Nicholas Ramdin',
      author_email='nicholas.ramdin@torch.ai',
      packages=['gateway_api'],
	install_requires= [
	'requests'
	]
     )