echo "BUILD START"
apt-get update
apt-get install -y python3 python3-pip python3-venv
apt-get install -y libpq-dev
python3.12 -m venv venv
source venv/bin/activate
pt-get install -y python3 python3-pip
pip install -r requirements.txt
python3.12 manage.py collectstatic --noinput
echo "BUILD END"