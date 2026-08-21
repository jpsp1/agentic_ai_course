#!/bin/bash
d=`date`
git config --global user.name "joao.pagaime@gmail.com"
git config user.name "joao.pagaime@gmail,com"
git config user.email "joao.pagaime@gmail.com"
git commit -m "updates a $d" -a
git push -u origin main
