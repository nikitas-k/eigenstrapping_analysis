#!/usr/bin/env bash
#
# Description:
#
#     This script is used to generate a Singularity container that can be used
#     to run all the analyses reported in our manuscript.
#
#     This script was initially written to be used on a Linux box running
#     Ubuntu 18.04.
#
# Usage:
#
#     $ bash container/gen_simg.sh
#

curr_dir=$PWD && if [ ${curr_dir##*/} = "container" ]; then cd ..; fi
tag=eigenstrapping_analysis

# use neurodocker (<3) to make a Docker recipe and build the Docker
# image. this should only happen if the image doesn't already exist
if [ ! -f container/${tag}.simg ]; then
  if [ ! -f container/license.txt ]; then touch container/license.txt; fi
  docker run repronim/neurodocker:0.7.0                                       \
    generate docker                                                           \
    -b ubuntu:18.04                                                           \
    --pkg-manager apt                                                         \
    --workdir $PWD                                                            \
    --install                                                                 \
      git less nano make connectome-workbench gmsh                            \
    --freesurfer                                                              \
      version=6.0.0-min                                                       \
      license_path=container/license.txt                                      \
      exclude_paths=subjects/V1_average                                       \
    --copy ./environment.yml /opt/environment.yml                             \
    --miniconda                                                               \
      create_env=${tag}                                                       \
      yaml_file=/opt/environment.yml                                          \
    --run "bash -c 'source activate ${tag}'"                                  \
    --add-to-entrypoint "source activate ${tag}"                              \
  > container/eigenstrapping_analysis.Dockerfile
  sudo docker build --tag eigenstrapping_analysis --output type=tar,dest=container/eigenstrapping_analysis.tar.gz --file container/eigenstrapping_analysis.Dockerfile .
fi