#!/bin/bash
# This shell script deploys a new version to a server.

PROJ_DIR=jlsa-fall-journal
VENV=swe-venv
PA_DOMAIN="sejutimannan.pythonanywhere.com"
PA_USER='sejutimannan'
echo "Project dir = $PROJ_DIR"
echo "PA domain = $PA_DOMAIN"
echo "Virtual env = $VENV"

if [ -z "$DEMO_PA_PWD" ]
then
    echo "The PythonAnywhere password var (DEMO_PA_PWD) must be set in the env."
    exit 1
fi

if [ -z "$API_TOKEN" ]
then
    echo "The API_TOKEN var must be set in the env."
    exit 1
fi

echo "PA user = $PA_USER"
echo "PA password = $DEMO_PA_PWD"

echo "SSHing to PythonAnywhere."
sshpass -p $DEMO_PA_PWD ssh -o "StrictHostKeyChecking no" $PA_USER@ssh.pythonanywhere.com << EOF
    # Export the API_TOKEN so it's available in PythonAnywhere
    export API_TOKEN="$API_TOKEN"
    # Navigate to project directory
    cd ~/$PROJ_DIR
    # Run rebuild script
    PA_USER=$PA_USER PROJ_DIR=~/$PROJ_DIR VENV=$VENV PA_DOMAIN=$PA_DOMAIN ./rebuild.sh
EOF
