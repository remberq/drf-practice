run:
	python manage.py runserver
mig:
	python manage.py makemigrations
migrate:
	python manage.py migrate
shell:
	python manage.py shell_plus --ipython
test:
	coverage run --source='.' manage.py test .
rep:
	coverage report
