def add_reading_metrics(books):
    books["ReadingTime"] = (books["FinishedDate"] - books["StartedDate"]).dt.days + 1
    books["ReadingSpeed"] = books['Pages']/books["ReadingTime"]

    books["ReadingSlump"] = books["ReadingSpeed"] < books["ReadingSpeed"].median() * 0.5

def mean_median(series) -> dict:
    return {"mean": series.mean(), "median": series.median()}


def extreme_row(df, column: str, mode: str, fields: dict) -> dict:
    """
    Find the row where 'column' is max/min and extract 'fields' from it.

    'fields' maps the output key -> the dataframe column to pull
    'mode' is "max" or "min".
    """
    idx = df[column].idxmax() if mode == "max" else df[column].idxmin()
    row = df.loc[idx]
    return {key: row[col] for key, col in fields.items()}


def compute_stats(books) -> dict:
    """
    Compute statistics from the books dataframe and return them as a dict.

    Returns:
        A dictionary containing the computed statistics.

    Raises:
        ValueError: if 'books' is empty or missing any required column.
    """
    REQUIRED_COLUMNS = [
            "StartedDate",
            "FinishedDate",
            "Rating",
            "PersonalScore",
            "EaseReading",
            "Language",
            "Pages",
            "ReadingTime",
            "ReadingSpeed",
            "ReadingSlump",
            "Title",
        ]
    
    if books.empty:
        raise ValueError("'books' is empty")

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in books.columns]
    if missing_columns:
        raise ValueError(
            f"'books' is missing required columns: {', '.join(missing_columns)}"
        )

    stats = {}

    stats["first_started"] = books["StartedDate"].min().strftime("%d/%m/%Y")
    stats["last_finished"] = books["FinishedDate"].max().strftime("%d/%m/%Y")
    stats["num_books"] = books.shape[0]

    stats["rating"] = mean_median(books["Rating"])
    stats["enjoyment"] = mean_median(books["PersonalScore"])

    rating_fields = {"title": "Title", "rating": "Rating", "enjoyment": "PersonalScore"}
    stats["best_rated"] = extreme_row(books, "Rating", "max", rating_fields)
    stats["worst_rated"] = extreme_row(books, "Rating", "min", rating_fields)

    stats["ease"] = mean_median(books["EaseReading"])

    ease_fields = {"title": "Title", "ease": "EaseReading"}
    stats["ease_by_language"] = {}
    for language, group in books.groupby("Language"):
        if group.empty:
            continue

        stats["ease_by_language"][language] = {
            **mean_median(group["EaseReading"]),
            "easiest": extreme_row(group, "EaseReading", "max", ease_fields),
            "hardest": extreme_row(group, "EaseReading", "min", ease_fields),
        }

    stats["pages"] = mean_median(books["Pages"])

    pages_fields = {"title": "Title", "pages": "Pages"}
    stats["longest"] = extreme_row(books, "Pages", "max", pages_fields)
    stats["shortest"] = extreme_row(books, "Pages", "min", pages_fields)

    stats["reading_time"] = mean_median(books["ReadingTime"])
    stats["reading_speed"] = mean_median(books["ReadingSpeed"])

    pace_fields = {
        "title": "Title",
        "pages": "Pages",
        "reading_time": "ReadingTime",
        "reading_speed": "ReadingSpeed",
    }
    stats["fastest"] = extreme_row(books, "ReadingSpeed", "max", pace_fields)

    slump_books = books[books["ReadingSlump"]]
    normal_books = books[~books["ReadingSlump"]]

    stats["has_slump"] = not slump_books.empty

    if slump_books.empty:
        stats["slowest_overall"] = extreme_row(books, "ReadingSpeed", "min", pace_fields)
    else:
        stats["slowest_slump"] = extreme_row(slump_books, "ReadingSpeed", "min", pace_fields)

        if not normal_books.empty:
            stats["slowest_normal"] = extreme_row(normal_books, "ReadingSpeed", "min", pace_fields)

    return stats

def analyse_books(books):
    add_reading_metrics(books)

    return compute_stats(books)