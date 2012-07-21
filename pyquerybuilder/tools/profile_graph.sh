#!/usr/local/bin/bash
for file in $(find  /tmp/ -name "profile*" )
do
    $QB_ROOT/pyquerybuilder/tools/gprof2dot.py -f pstats $file | dot -Tpng -o $file.png
done

