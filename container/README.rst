Replicating analyses with a Docker image
========================================

This directory contains files to generate a Docker container that can be used to re-run the analyses in the paper without the need to install extra software or re-invent the wheel (beyond Docker, of course). You can download the image on `OSF <https://osf.io/download/hv7q5>`_

* `gen_docker.sh`: this script generates the Docker image
* `eigenstrapping_analysis.Dockerfile`: the Docker build target generated from `gen_docker.sh` used to build the Docker image

Once you've `downloaded <https://osf.io/download/hv7q5>`_ (and put the image in this directory) or built the Docker image by running `sh gen_docker.sh`, in order to reproduce the analyses, run the following:

.. code-block:: bash

    docker import container/eigenstrapping_analysis.tar.gz eigenstrapping_analysis:latest &\
        docker run -w ${PWD} -it eigenstrapping_analysis                                   \
        /neurodocker/startup.sh                                                            \
        make all

If you get errors like `permission denied while trying to connect to the Docker daemon socket` and so on, try running the above with `sudo` prepended to the `docker` commands. Also, this will take a very long time unless you're running it on a HPC! Try to run the `make` with other options (see `here :ref:<../README.rst>`)

NOTE: If you do build the image manually with `gen_docker.sh`, you will need to source your own Freesurfer license file and place it in this folder.