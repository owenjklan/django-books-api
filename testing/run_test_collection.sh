#!/bin/bash

if [ $# -ne 1 ]; then
  echo -e "\033[31mError! You must provide a collection name!\033[0m"
  echo -e "\n\tUSAGE: $0 <collection>\n"
  echo "Launch Newman, running <collection>.collection.json as a Postman collection,"
  echo "using <collection>.environment.json as the Environment for the run."
  echo "This means that 'collection name' is a component of files on disk and not"
  echo "the name of the collection as it would be visible in the Postman application."

  exit 1
fi

COLLECTION_NAME=$1

COLLECTION_FILE="${COLLECTION_NAME}.collection.json"
ENVIRONMENT_FILE="${COLLECTION_NAME}.environment.json"

if [ ! -f ${COLLECTION_FILE} ]; then
  echo -e "\033[31mError! Requested collection not found: ${COLLECTION_FILE}"
  echo "Are you launching from the correct directory?"
  exit 1
fi

if [ ! -f ${ENVIRONMENT_FILE} ]; then
  echo -e "\033[31mError! Requested environment not found: ${ENVIRONMENT_FILE}"
  echo "Are you launching from the correct directory?"
  exit 1
fi

# Double check for 'newman'
echo "Checking for Newman installation..."
newman --version

if [ $? -ne 0 ]; then
  echo -e "\033[31mError! Failed running Newman. Is it installed?\033[0m"
  echo ""
  echo "To install Newman, ensure that NodeJS and NPM are installed on your system."
  echo -e "Then, run \033[33;1mnpm install -g newman\033[0m to install the newman package."

  exit 1
fi

# Attempt run
newman run ${COLLECTION_FILE} --environment ${ENVIRONMENT_FILE}
