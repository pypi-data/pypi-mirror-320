from setuptools import setup

from benutils.version import __version__

setup(name='benutils',
      description='Various utilities (mjd, data container, widgets...)',
      version=__version__,
      packages=['benutils.misc',
                'benutils.widget',
                'benutils.sdr'],
      install_requires=['numpy'],
      extras_require = {
          'usb_utils_support': ['pyusb'],
          'Pure_Python_signalslot_facilities': ["signalslot"],
          'PyQt_signalslot_facilities': ["PyQt5"],
          'real_time_plot_support': ["pyqtgraph"]
      },
      url='https://gitlab.com/bendub/benutils',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-engineering.fr',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering'],
)
