#!/bin/sh
# one worker per argument list of config indices
cd /home/user/469
for i in "$@"; do
  python -u experiments/e_c_homophonic/run_c.py "$i" >> experiments/e_c_homophonic/results_c/driver.log 2>&1
done
