python -m venv tempvenv
source tempvenv/bin/activate
pip install -r REQUIREMENTS-for-aws.txt
cd tempvenv/lib/python3.12/site-packages
zip -r9 ../../../../my_deployment_package_generated.zip .
cd -
cd src
cat for_aws.txt | xargs zip -g ../my_deployment_package_generated.zip
deactivate
cd ..
rm -rf tempvenv