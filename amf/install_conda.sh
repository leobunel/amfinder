#! /bin/bash

conda create -p ./amfenv python=3.9 && \
conda activate ./amfenv && \
python -m pip install --upgrade pip && \
python -m pip install -r requirements.txt && \
conda deactivate

RETURN=$?

if [ $RETURN -eq 0 ];
then
  echo "The AMFinder tool <amf> was successfully installed."
  exit 0
else
  echo "Installation failed. Known issues:"
  echo "- installation may fail if ~/.local/lib/python folders exist"
  echo "  these are usually left by previous installations, consider deleting them"
  echo "  see https://github.com/conda/conda/issues/11279"
  echo "- sometimes conda does not get exported to bash subshells"
  echo "  a workaround is to run <source install_conda.sh> instead"
  exit $RETURN
fi
