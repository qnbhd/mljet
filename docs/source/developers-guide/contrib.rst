=======
Contrib
=======

**MLJET** `contrib` directory contains a set of scripts needed for
final project build and mljetnt.

Now is supported next targets:

* **Local** - build and deploy project to local machine (save or run
  project)
* **Docker** - build and deploy project to Docker container

**Contrib** has next structure:

.. code::

    ├── analyzer.py             -- Module for analyze ML model's methods
    ├── docker_                 -- Docker target folder
    │   ├── docker_builder.py   -- Docker mljetnt target
    │   └── runner.py           -- Docker runner
    ├── entrypoint.py           -- Main project entrypoint
    ├── local.py                -- Local mljetnt target
    ├── project_builder.py      -- Project builder
    ├── supported.py            -- List of supported models, targets, etc.
    └── validator.py            -- Project validator

-----------
Description
-----------

* **analyzer.py** - Module for analyze ML model's methods (extract
  methods names, etc.) and find associated wrapper to paste it into
  backend template.
* **docker/_** - folder with Docker target scripts
* **docker/_builder.py** - script for build and deploy project to Docker
  container
* **runner.py** - Module for build, run and stop Docker container
* **entrypoint.py** - Main project entrypoint, contains main `cook` function
* **local.py** - Module for build and deploy project to local machine
* **project_builder.py** - Module for build project
* **supported.py** - List of supported models, targets, etc.
* **validator.py** - Module for validate project
