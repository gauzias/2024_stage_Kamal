#!/bin/bash
input_image=$1
output_image=$2
fslcpgeom  $input_image $output_image
