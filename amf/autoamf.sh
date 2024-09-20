#!/bin/bash

usage='Usage: ./autoamf.sh [-1 CNN1_NETWORK] [-2 CNN2_NETWORK] [-s THRESHOLD] [-t TILE_SIZE] FILE...'

# Set options defaults.
cnn1_network="CNN1v2.h5"
cnn2_network="CNN2v2.h5"
threshold=0.5
tile_size=126

# Detect options (see Usage).
while getopts '1:2:s:t:' flag; do
  case "${flag}" in
    1) cnn1_network="${OPTARG}" ;;
    2) cnn2_network="${OPTARG}" ;;
    s) threshold="${OPTARG}" ;;
    t) tile_size="${OPTARG}" ;;
    *) echo "${usage}" >&2 && exit 3 ;;
  esac
done

# Verify that at least 1 file has been provided.
if [ $(( $# - (OPTIND - 1) )) -lt 1 ]; then
  echo "${usage}" >&2
  exit 4
fi

source amfenv/bin/activate

# Predict fungal colonisation (CNN1) on a bunch of JPEG or TIFF images.
./amf predict --network "${cnn1_network}" --tile_size "${tile_size}" "${@:$OPTIND}"

# Convert CNN1 predictions to annotations.
./amf convert --CNN1 "${@:$OPTIND}"

# Predict intraradical structures (CNN2) on the same images.
./amf predict --network "${cnn2_network}" --tile_size "${tile_size}" "${@:$OPTIND}"

# Convert CNN2 predictions to annotations using the specified threshold.
./amf convert --CNN2 --threshold "${threshold}" "${@:$OPTIND}"

deactivate
