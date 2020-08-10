Linux Install:
    sudo apt install libboost-all-dev
    sudo cp ./src/xem_wrapper/_linux/libokFrontPanel.so /usr/local/lib/

MacOS Install:
    install_name_tool -change libokFrontPanel.dylib /usr/local/lib/libokFrontPanel.dylib _ok.so
    sudo cp ./src/xem_wrapper/_mac/libokFrontPanel.dylib /usr/local/lib/


.. image:: https://img.shields.io/pypi/v/xem-wrapper.svg
    :target: https://pypi.org/project/xem-wrapper/

.. image:: https://pepy.tech/badge/xem-wrapper
  :target: https://pepy.tech/project/xem-wrapper

.. image:: https://img.shields.io/pypi/pyversions/xem-wrapper.svg
    :target: https://pypi.org/project/xem-wrapper/

.. image:: https://github.com/CuriBio/xem-wrapper/workflows/Dev/badge.svg?branch=development
   :alt: Development Branch Build

.. image:: https://codecov.io/gh/CuriBio/xem-wrapper/branch/development/graph/badge.svg
  :target: https://codecov.io/gh/CuriBio/xem-wrapper

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. image:: https://codecov.io/gh/CuriBio/xem-wrapper/branch/development/graph/badge.svg
  :target: https://codecov.io/gh/CuriBio/xem-wrapper
