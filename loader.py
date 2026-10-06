import pandas as pd

def column_mapping(books):
    books.rename(columns={
        "Name": "Title",
        "Original Title": "OriginalTitle",
        "Author(s)":"Authors",
        "Genre(s)":"Genres", 
        "Other tags":"Tags", 
        "First published":"YearPublished", 
        "Started Reading":"StartedDate",
        "Finished Reading":"FinishedDate",
        "Ease of reading":"EaseReading",
        "How much I liked it":"PersonalScore",
        "Edition language":"Language",
        "Goodreads' page":"GoodreadsURL",
        "Part of series":"InSeries"
        }, inplace=True)
    
    return books

def clean_data(books):

    column_mapping(books)

    # dropping books i did not finish
    books.drop(books[books["DNF"] == "Yes"].index, inplace=True)
    books.drop(books[books["Status"] != "✅ Finished"].index, inplace=True)
    books.drop(columns=["Status","DNF"], inplace=True)
    
    # handling missing data 
    books["OriginalTitle"] = books["OriginalTitle"].fillna(books["Title"])

    # multi-values fields data splitting
    books["Genres"] = books["Genres"].str.split(", ")
    books["Authors"] = books["Authors"].str.split(", ")
    books["Tags"] = books["Tags"].str.split(", ")

    # data conversions
    books["StartedDate"] = pd.to_datetime(
        books["StartedDate"],
        format="%B %d, %Y"
    )

    books["FinishedDate"] = pd.to_datetime(
        books["FinishedDate"],
        format="%B %d, %Y"
    )

    books["Reread"] = books["Reread"].map({
        "Yes": True,
        "No": False
    }).astype("boolean")

    books["InSeries"] = (
        books["InSeries"]
        .fillna("")
        .str.strip()
        .ne("")
        .astype("boolean")
    )

    books["Rating"] = books["Rating"].str.extract(r"(\d+)").astype("Int64")

    return books


def load_books(path, end_date = None):
    data = pd.read_csv(path)

    n_loaded = data.shape[0]
    
    if n_loaded != 0:
        print(n_loaded, "books loaded.")
        books = clean_data(data)

        if end_date is not None:
            try:
                end_date = pd.to_datetime(end_date, format="%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date. Use YYYY-MM-DD.")
            
            books = books[books["FinishedDate"] >= end_date]

            print(f"{books.shape[0]} books left after date filtering (only books finished after {end_date}).")
            print()
    else:
        print("Error loading data.")
        print()

    return books