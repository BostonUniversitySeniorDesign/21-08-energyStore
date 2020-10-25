


daemon_file='empty' #fill this out
working_dir=$(pwd)

echo "[Service]" | sudo tee -a $daemon_file
echo "WorkingDirectory" #finish
echo "ExecStart=/usr/bin/python3.8 $finmain.py" | sudo tee -a $daemon_file
echo "Restart=always" | sudo tee -a $daemon_file
