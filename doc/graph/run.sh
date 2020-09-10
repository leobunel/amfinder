#! /bin/bash

cd ../..

ocamldep -one-line *.ml *.mli \
  | grep -v "cmx" \
  | ./doc/graph/mkgraph.py \
  | tee ./doc/graph/dep_graph.dot \
  | dot -Tpng > ./doc/graph/dep_graph.png
