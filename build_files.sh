echo "BUILD START"
apt-get update
apt-get install -y python3 python3-pip python3-venv
apt-get install -y libpq-dev
python3.12 -m venv venv
source venv/bin/activate
pt-get install -y python3 python3-pip
pip3 install -r requirements.txt
echo "BUILD END"