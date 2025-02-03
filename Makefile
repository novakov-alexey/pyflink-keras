create-env:
	conda create --prefix ./ann python=3.10
	conda activate ./ann

install-macos:
	conda install -c apple -c conda-forge -c nodefaults tensorflow-deps
	# Tensorflow version can be tuned as per your OS and CPU version
	python -m pip install tensorflow-macos==2.10.0
	python -m pip install tensorflow-metal==0.6.0
	conda install pandas scikit-learn
	python -m pip install apache-flink==1.19.1

install-linux:	
	conda install --file linux-requirements.txt
	python -m pip install apache-flink==1.19.1

local-run:
	python flink_ann.py