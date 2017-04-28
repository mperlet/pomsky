#!/bin/bash

if [ -z "$PYTHON" ]; then
  PYTHON=python
fi

timeout 5s $PYTHON pomsky.py &
sleep 1

curl -s http://localhost:8888 > /dev/null
CURL_RETURN_VALUE=$?
if ([ $CURL_RETURN_VALUE -ne "0" ]);then
  echo "main page failed"
  exit 1
fi


curl -s http://localhost:8888 --data 'input=Hello+World' > /dev/null
CURL_RETURN_VALUE_DATA=$?
if ([ $CURL_RETURN_VALUE_DATA -ne "0" ]);then
  echo "post request failed"
  exit 1
fi

cat /tmp/pomsky.txt | grep "Hello World" > /dev/null
WRITE_FILE=$?
echo "" > workingfile.txt
if ([ $WRITE_FILE -ne "0" ]);then
  echo "File contains wrong data"
  exit 1
fi

curl -s http://localhost:8888/run0 > /dev/null
CURL_RETURN_VALUE_RUN=$?
if ([ $CURL_RETURN_VALUE_RUN -ne "0" ]);then
  echo "Run command failed"
  exit 1
fi

wait $!
POMSKY_RETURN_VALUE=$?
if ([ $POMSKY_RETURN_VALUE -ne "124" ]);then
  echo "pomsky failed command failed"
  exit 1
fi

exit 0
