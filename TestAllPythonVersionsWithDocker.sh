#!/bin/bash

docker build -t pomsky .

declare -a python_versions=("python2.3" "python2.4" "python2.7" "python3.3" "python3.4" "python3.5" "python3.6" "pypy")

for python_version in "${python_versions[@]}"
do
   docker run -e PYTHON=$python_version -p8888:8888 pomsky

   if ([ $? -eq "0" ]);then
     echo "OK   $python_version"
   else
     echo "FAIL $python_version"
   fi
done
