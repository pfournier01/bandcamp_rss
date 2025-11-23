#!/usr/bin/bash

# TODO: check Python install
# and install .venv locally if needed
# (please prompt user)

######### Checking Python version
TARGET_PY_VERSION=3.11.0
which python
HAS_PYTHON=$?
if [[ $HAS_PYTHON -ne 0 ]]; then
    echo "Could not find a Python installation. Aborting."
    return 1
else
    PY_VER=python -V | grep -Eo [0-9]*\.[0-9]*\.[0-9]*$
    # if PY_VER < TARGET_PY_VERSION
    if [[ $($PY_VER $TARGET_PY_VERSION | sort -V | cut -d " " -f1) == $PY_VER && $PY_VER != $TARGET_PY_VERSION ]]; then
        echo "Current Python version is too small. Found $PY_VER, excepted $TARGET_PY_VERSION or higher. Aborting."
        return 2
    fi
fi
######## Checking dependencies
packages=$(pip list --format=freeze)
required_packages=$(cat requirements.txt)
all_satisfied=0
for req_package in "${required_packages[@]}"; do
    package_name=$(echo $req_package | grep -Eo "^[^<=>]*")
    package_req_ver=$(echo $req_package | grep -Eo "^[^<=>]*$")
    package_ver_comp=$(echo $req_package | grep -Eo "[<=>]*")
    package_spec=$(echo $packages | grep -Eo $package_name | tail -n1)
    package_ver=$(echo $package_spec | grep -Eo "[^<=>]*$")
    if [[ -z $package_ver ]]; then
        satisfied=1
        echo "Package $package_name not found in current installation."
    elif [[ $package_ver_comp == "==" ]]; then
       [[ $package_req_ver == $package_ver ]]
       satisfied=$?
    elif [[ $package_ver_comp == "<=" ]]; then
        [[ $($package_req_ver $package_ver | sort -V | cut -d " " -f1) == $package_ver ]]
        satisfied=?$
    elif [[ $package_ver_comp == "<" ]]; then
        [[ $($package_req_ver $package_ver | sort -V | cut -d " " -f1) == $package_ver && $package_ver != $package_req_ver ]]
        satisfied=?$
    elif [[ $package_ver_comp == ">" ]]; then
        [[ $($package_req_ver $package_ver | sort -V | cut -d " " -f2) == $package_ver && $package_ver != $package_req_ver ]]
        satisfied=$?
    elif [[ $package_ver_comp == ">=" ]]; then
        [[ $($package_req_ver $package_ver | sort -V | cut -d " " -f2) == $package_ver ]]
        satisfied=$?
    else
        echo "Unknown version comparison operator $package_ver_comp encountered for package $package_name. Aborting"
        return 3
    fi

    if [[ $satisfied -ne 0 ]]; then
        all_satisfied=1
        echo "Package $package_name does not satisfy version requirements. Required $package_ver_comp $package_req_ver, found $package_ver"
    fi
done

####### Not all dependencies are good, propose to install venv
if [[ $all_satisfied -ne 0 ]]; then
    input_value=""
    echo "The current Python environment is not suitable, dependencies are not good. Do you wish to:
        (1) [Default] create a new local virtual environment
        (2) try install them in the current
        (3) abort"
    while [[ $input_value != 1 || $input_value != 2 || $input_value != 3 ]]; do
        read input_value
    done
    if [[ $input_value == 3 ]]; then
        echo "Aborting"
        return 4
    elif [[ $input_value == 2 ]]; then
        # create the venv
        python -m venv .venv
        . .venv/bin/activate
        pip install -r requirements.txt
    elif [[ $input_value == 1 ]]; then
        # install the packages
        pip install -r requirements.txt
        output=$?
        if [[ $output -ne 0 ]]; then
            echo "The installation of the packages in the current environment has failed, please install them manually or try another method"
            return 5
        fi
    fi
    
    
fi


    



# TODO: generate an uninstall metadata file
# to know whether the .venv got created or not
#
# TODO: create concrete service file
# TODO: enable systemd unit files (service & timer)
