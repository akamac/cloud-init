from setuptools import setup, find_packages

setup(name='cloudinit',
      version='0.3.4',
      description='Framework for early Linux guest initialization',
      url='https://github.com/akamac/cloud-init',
      author='Alexey Miasoedov',
      author_email='alexey.miasoedov@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6'],
      keywords='cloud-init initialization ubuntu debian',
      packages=find_packages(),  # ['cloudinit', 'cloudinit.plugins'],
      entry_points={
          'console_scripts': [
              'cloud-init = cloudinit.__main__:main'
          ]
      },
      zip_safe=False)
