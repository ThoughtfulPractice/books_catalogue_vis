import requests
import pandas as pd
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define input and output file names
input_file = 'raw_data_books.csv'
output_file = '301_fetch_book_info.csv'


def fetch_book_info(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    response = requests.get(url)
    data = response.json()

    if f"ISBN:{isbn}" in data:
        book_data = data[f"ISBN:{isbn}"]
        has_fetched_data = 1
        title = book_data.get("title", "N/A")
        authors = ", ".join(author["name"] for author in book_data.get("authors", []))
        cover_url = book_data.get("cover", {}).get("large", "N/A")
        publish_date = book_data.get("publish_date", "N/A")
        number_of_pages = book_data.get("number_of_pages", "N/A")

        # Extract the year from the publish_date
        if publish_date != "N/A":
            match = re.search(r'\d{4}', publish_date)
            if match:
                publish_date = match.group(0)
            else:
                publish_date = "N/A"

    else:
        has_fetched_data = 1
        title = "N/A"
        authors = "N/A"
        cover_url = "N/A"
        publish_date = "N/A"
        number_of_pages = "N/A"

    return {
        "has_fetched_data": 1,
        "title": title,
        "author": authors,
        "book_cover_url": cover_url,
        "publish_date": publish_date,
        "number_of_pages": number_of_pages,

    }


def main():
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Initialize new columns
    new_columns = ["has_fetched_data", "title", "author", "book_cover_url", "publish_date",
                   "number_of_pages"]
    for col in new_columns:
        if col not in df.columns:
            df[col] = ""

    # Fetch additional information for each ISBN
    total_books = len(df)
    for index, row in df.iterrows():
        isbn = row['ISBN']

        # Check if the data is already filled in
        if row['has_fetched_data'] != 1:
            book_info = fetch_book_info(isbn)
            for key, value in book_info.items():
                df.at[index, key] = value

        # Log progress
            progress = (index + 1) / total_books * 100
            logging.info(f'Completed {progress:.2f}% - Last completed book: {book_info["title"]}')

    # Save the new DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    logging.info(f'Completed processing all books. The output file is saved as {output_file}.')


if __name__ == "__main__":
    main()
