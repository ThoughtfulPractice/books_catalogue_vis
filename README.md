# Visualising My Books

I created a catalogue of my books, and visualised the data associated with them.

## Raw Data
data/raw/books.csv was manually created. You can replace this with your own book catalogue if you wish.

## Getting Started

1. As we are calling for data using the googlebooks API, create a *.env* file in the project root folder. We only need one line:
```
GOOGLEBOOKS_API_KEY=[Your personal API key here. DO NOT SHARE THIS!]
```

2. We are collecting data from two sources. In the terminal, run the following Python scripts. It save the data in the *data/external* folder.
```
$ python get_googlebooks_data.py
$ python get_openlibrary_data.py
```

3. Run the following Python script to merge and create the dataset for data visualisation.
```
$ python tidy_books_data.py
```
