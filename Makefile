prod:
	apt-get install sudo
	apt-get install -y python3 python3-pip
	pip3 install --upgrade pip
	pip3 install -r requirements.txt
	apt-get install -y postgresql
	apt-get install -y postgresql-contrib
	export DB_USER=user_db DB_PASSWORD=123456789
	export SECRET_KEY="g5kl0(6*_xpg)=f*cz3)&eg0m#g6bwa^dlct%yh2arvo4nyl_1"
	export HASKER_SERVICE_MAIL=yoko11.06.92@yandex.ru
	service postgresql start
	sudo -u postgres psql -f deploy/setup_db.sql -v user=user_db -v pwd=123456789
	apt-get install -y nginx
	rm -f /etc/nginx/sites-enabled/default
	cp deploy/hasker_nginx.conf /etc/nginx/conf.d/hasker_nginx.conf
	cp deploy/uwsgi_params uwsgi_params
	/etc/init.d/nginx start
	python3 manage.py makemigrations
	python3 manage.py migrate
	uwsgi --ini deploy/hasker_uwsgi.ini
