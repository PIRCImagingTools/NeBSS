#!/bin/bash

FSLDIR=/usr/share/fsl/5.0 
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH

case "$1" in 
config)
exec python /app/create_config.py "$2" 
;;
*config.json)
exec python /app/nebss_cl.py "$@" 
;;
*.nii*)
eval python /app/generate_config.py "$@"
config_file=$(ls -t | grep config.json | head -n 1)
if [ -e "$config_file" ]; then
    eval python /app/nebss_cl.py "$config_file"
fi
;;
*)
echo "No config or image file found. Entering command mode. 

To create a config file: 
<NeBSS_Command> config <input_image.nii.gz> 

To view nipype crash file: 
nipypecli crash <crash file> 

Exit with CTRL+D
"
bash 
;;
esac

