# For 'make python'
python_loc=$(shell which python3.8)
pip_loc=$(shell which pip3)

# For 'make daemon'
daemon_file=empty



### make everything ###
all: python daemon

### print a list ###
list:
	@echo "make all"
	@echo "          install python, required dependencies, and set up system daemon"
	@echo "make python"
	@echo "          install python and the required dependencies"
	@echo "make daemon"
	@echo "          set up main.py as a system daemon"
	@echo "make clean"
	@echo "          remove client_log"

### Setup required to make the python work ###
python:
	dpkg -s python3.8 || sudo -H apt install python3.8
	dpkg -s python3-pip || sudo -H apt install python3-pip
	sudo -H $(python_loc) $(pip_loc) install --upgrade pip
	$(python_loc) $(pip3_loc) list | grep gpiozero || sudo -H $(python_loc) $(pip_loc) install gpiozero
	#sudo usermod -a -G gpio $(USER)

### setup required to run the above python as a system daemon ###
daemon:
	@echo "need to fill this out"
	#echo "[Service]" | sudo tee -a $(daemon_file)

### clean up the log ###
clean:
	rm client_log
