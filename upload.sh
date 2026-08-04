#!/bin/bash
d=`date`
#$ git config user.email "joao.pagaime@gmail.com"
git commit -m "updates a $d" -a
git push -u origin main
