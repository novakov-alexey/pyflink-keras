create-env:
	conda create --prefix ./ann python=3.8
	conda activate ./ann

install-macos:
	conda install -c apple -c conda-forge -c nodefaults tensorflow-deps
	python -m pip install tensorflow-macos==2.10.0
	python -m pip install tensorflow-metal==0.6.0
	conda install pandas scikit-learn
	python -m pip install apache-flink==1.18.1

install-linux:
	python -m pip install tensorflow
	conda install pandas scikit-learn
	python -m pip install apache-flink==1.18.1

local-run:
	python flink_ann.py