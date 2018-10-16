# Visualising My Books

I created a catalogue of my books, and visualised the data associated with them.

## Raw Data
data/raw/books.csv was manually created. You can replace this with your own book catalogue if you wish.

## Getting Started
1. After cloning the project, create the environment by running the following line in the project root directory:
```
$ make create_environment
```
This installs pipenv in your local user directory, creates a virtual environment using pipenv, and enters the environment shell automatically.

2. If you are using your own data/raw/books.csv file:

	A. Create a *.env* file in the project root folder:
	```
	$ GOOGLEBOOKS_API_KEY='<Your personal API key here. DO NOT SHARE THIS!>'
	```
	B. Then, run the following to call data from two sources: googlebooks API and Open Library books API.
	```
	$ make api
	```

3. After the data has been collected, run the following to tidy the datasets and merge them:
```
$ make data
```
4. The following command will create the data visualisations in the project:
```
$ make vis
```
