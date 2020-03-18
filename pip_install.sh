#!/usr/bin/env bash

pip_install_save() {
    package_name=$1
    requirements_file='./requirements.txt'
    pip3 install --upgrade ${package_name} && pip3 freeze | grep ${package_name} >> ${requirements_file}
}



pip_install_save $1