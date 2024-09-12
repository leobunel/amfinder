#!/bin/bash

USAGE='Usage: ./autoamf [-t THRESHOLD] FILE...'
readonly USAGE

# Use the -t option to set the CNN2 threshold (0.5 by default).
THRESHOLD=0.5
while getopts 't:' flag; do
  case "${flag}" in
    t) THRESHOLD="${OPTARG}" ;;
    *) echo "${USAGE}" >&2 && exit 3 ;;
  esac
done
readonly THRESHOLD

# Verify that at least 1 file has been provided.
if [ $(( $# - (OPTIND - 1) )) -lt 1 ]; then
  echo "${USAGE}" >&2
  exit 4
fi

source amfenv/bin/activate

# Predict fungal colonisation (CNN1) on a bunch of JPEG or TIFF images.
./amf predict --network CNN1v2.h5 "${@:$OPTIND}"

# Convert CNN1 predictions to annotations.
./amf convert --CNN1 "${@:$OPTIND}"

# Predict intraradical structures (CNN2) on the same images.
./amf predict --network CNN2v2.h5 "${@:$OPTIND}"

# Convert CNN2 predictions to annotations using the specified threshold.
./amf convert --CNN2 --threshold "${THRESHOLD}" "${@:$OPTIND}"

deactivate
