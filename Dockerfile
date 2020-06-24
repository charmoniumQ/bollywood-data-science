	sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv postgrseql-client git tmux && git clone --branch feat-acquire-data https://github.com/charmoniumQ/bollywood-data-science && pip3 install poetry && cd bollywood-data-science && python3 -m poetry install && tmux
sudo apt-get install -y libpq-dev postgresql-client && python3 -m poetry install && tmux
git pull origin feat-acquire-data

poetry run python3 -m bollywood_data_science.main 0 920
poetry run python3 -m bollywood_data_science.main 920 1840
poetry run python3 -m bollywood_data_science.main 1840 2760
poetry run python3 -m bollywood_data_science.main 2760 3680
poetry run python3 -m bollywood_data_science.main 3700 4620
poetry run python3 -m bollywood_data_science.main 4620 5550
