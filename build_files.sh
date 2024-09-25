echo "BUILD START"
apt-get update
apt-get install -y python3 python3-pip
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3.12 manage.py collectstatic --noinput
echo "BUILD END"