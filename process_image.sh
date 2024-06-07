#!/bin/bash
input_image=$1
output_image=$2
fslswapdim  $input_image -x y -z  $output_image
