
# Used random number and words in the name to avoid conflicts
python -m venv tempvenvseetidypolite29632963
source tempvenvseetidypolite29632963/bin/activate
pip install -r REQUIREMENTS-for-aws.txt
cd tempvenvseetidypolite29632963/lib/python3.12/site-packages
zip -r9 ../../../../my_deployment_package_generated.zip .
cd -
cd src
cat for_aws.txt | xargs zip -g ../my_deployment_package_generated.zip
deactivate
cd ..
rm -rf tempvenvseetidypolite29632963