mkdir -p xunit-reports coverage-reports html-coverage
coverage run --rcfile=.coveragerc -m pytest --junit-xml=xunit-reports/xunit-result.xml
ret=$?
coverage xml -o coverage-reports/coverage.xml
coverage html -d html-coverage  
coverage report
exit $ret