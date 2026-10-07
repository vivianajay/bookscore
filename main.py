import argparse

import loader
import ratings
import analyser
import output

def main():
    default_path = "./data/books.csv"

    parser = argparse.ArgumentParser(
        prog='bookscore',
        description=(
            "Analyse a book dataset from a csv file and calculate recommended "
            "whole-number ratings based on reading experience, "
            "with optional interactive user evaluation."
        )
    )
    parser.add_argument("path", nargs='?', default=default_path, 
                        help=f"Path to the input CSV file (default: {default_path}).")

    parser.add_argument("--end-date", help="Only consider books finished on or after this date. Format: YYYY-MM-DD.")

    """
        available modes:
        - reading analysis only
        - rating recommendations only, with interactive user evaluation
        - rating recommendations only, without interactive user evaluation
        - both analysis and rating recommendations, with interactive user evaluation
        - both analysis and rating recommendations, without interactive user evaluation <- default
    """

    mode = parser.add_mutually_exclusive_group()

    mode.add_argument(
        "--analysis-only",
        action="store_true",
        help="Only calculate and print reading statistics.",
    )

    mode.add_argument(
        "--ratings-only",
        action="store_true",
        help="Only calculate rating recommendations.",
    )

    parser.add_argument(
        "--user-evaluation",
        action="store_true",
        help="Run the interactive user evaluation.",
    )

    parser.add_argument(
        "--save-output",
        action="store_true",
        help="Save generated reports and cleaned data to ./data/out.",
    )
    
    args = parser.parse_args()

    end_date = args.end_date
    save_output= args.save_output
    run_analysis = not args.ratings_only
    run_ratings = not args.analysis_only
    run_evaluation = args.user_evaluation

    books = loader.load_books(args.path, end_date)

    if run_analysis:
        stats = analyser.analyse_books(books)
        output.print_stats_report(stats, save_output)

    if args.save_output:
        output.save_clean_books_df(books)

    if run_ratings:
        if not run_analysis: analyser.add_reading_metrics(books) # add necessary additional metrics 

        recom_ratings = ratings.recomm_goodreads_rating(books)

        if run_evaluation:
            user_eval = ratings.recom_ratings_user_evaluation(books, recom_ratings)

            output.print_user_evaluation_results_report(user_eval, save_output)
        else:
            output.print_rating_recommendations(recom_ratings, save_output)


if __name__ == "__main__":
    main()
