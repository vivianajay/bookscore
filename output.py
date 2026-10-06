import datetime
from pathlib import Path

def print_stats_report(stats: dict, save_output : bool = False) -> str:
    """Format the computed stats dict into a readable report string and prints."""

    print("Reading stats:")
    parts = [
        f"Number of books read between {stats['first_started']} and "
        f"{stats['last_finished']}: {stats['num_books']}."
    ]

    parts.append(
        f"Average rating: {stats['rating']['mean']:.2f}/10, "
        f"median: {stats['rating']['median']}/10."
    )

    parts.append(
        f"Average enjoyment: {stats['enjoyment']['mean']:.2f}/5, "
        f"median: {stats['enjoyment']['median']}/5."
    )

    best = stats["best_rated"]
    parts.append(
        f'Highest-rated book: "{best["title"]}", '
        f'rated {best["rating"]}/10, '
        f'enjoyment {best["enjoyment"]}/5.'
    )

    worst = stats["worst_rated"]
    parts.append(
        f'Lowest-rated book: "{worst["title"]}", '
        f'rated {worst["rating"]}/10, '
        f'enjoyment {worst["enjoyment"]}/5.'
    )

    parts.append(
        f"Average ease of reading: {stats['ease']['mean']:.2f}/5, "
        f"median: {stats['ease']['median']}/5."
    )

    for language, lang_stats in stats["ease_by_language"].items():
        parts.append(
            f"Average ease of reading ({language}): {lang_stats['mean']:.2f}/5, "
            f"median: {lang_stats['median']}/5."
        )

        easiest = lang_stats["easiest"]
        hardest = lang_stats["hardest"]
        parts.append(
            f'Ease of reading ({language}): '
            f'easiest "{easiest["title"]}" ({easiest["ease"]}/5), '
            f'hardest "{hardest["title"]}" ({hardest["ease"]}/5).'
        )

    parts.append(
        f"Average book length: {stats['pages']['mean']:.2f} pages, "
        f"median: {stats['pages']['median']}."
    )

    longest = stats["longest"]
    parts.append(f'Longest book read: "{longest["title"]}", {longest["pages"]} pages.')

    shortest = stats["shortest"]
    parts.append(f'Shortest book read: "{shortest["title"]}", {shortest["pages"]} pages.')

    parts.append(
        f"Average reading time: {stats['reading_time']['mean']:.2f} days, "
        f"median: {stats['reading_time']['median']} days."
    )

    parts.append(
        f"Average reading speed: {stats['reading_speed']['mean']:.2f} pages/day, "
        f"median {stats['reading_speed']['median']} pages/day."
    )

    fastest = stats["fastest"]
    parts.append(
        f'Fastest reading pace: "{fastest["title"]}", '
        f'{fastest["pages"]} pages read in {fastest["reading_time"]} days '
        f'({fastest["reading_speed"]:.2f} pages/day).'
    )

    if not stats["has_slump"]:
        slowest = stats["slowest_overall"]
        parts.append(
            f'Slowest reading pace: "{slowest["title"]}", '
            f'{slowest["pages"]} pages read in {slowest["reading_time"]} days '
            f'({slowest["reading_speed"]:.2f} pages/day).'
        )
    else:
        slowest_slump = stats["slowest_slump"]
        parts.append(
            f'Slowest reading pace (in a reading slump): '
            f'"{slowest_slump["title"]}", '
            f'{slowest_slump["pages"]} pages read in '
            f'{slowest_slump["reading_time"]} days '
            f'({slowest_slump["reading_speed"]:.2f} pages/day).'
        )

        if "slowest_normal" in stats:
            slowest_normal = stats["slowest_normal"]
            parts.append(
                f'Slowest reading pace (not in a reading slump): '
                f'"{slowest_normal["title"]}", '
                f'{slowest_normal["pages"]} pages read in '
                f'{slowest_normal["reading_time"]} days '
                f'({slowest_normal["reading_speed"]:.2f} pages/day).'
            )

    report = "\n".join(parts)
    print(report,"\n")
    
    if save_output:
        print("Saving reading stats report...")
        save_reading_stats_report(report)

def save_reading_stats_report(report):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"reading_stats_{timestamp}.txt"
    output_dir = Path("./data/out")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(f"{output_dir}/{filename}", "w") as text_file:
        text_file.write(report)

    print("Reading stats report saved to txt file.\n")

def save_clean_books_df(books):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    output_dir = Path("./data/out")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"books_clean_{timestamp}.csv"
    outpath = output_dir / filename
    books.to_csv(outpath, index=False)
    print(f"Cleaned books data saved to csv.\n")

def print_rating_recommendations(recom, save_output = False):
    print("Rating recommendations:")
    print(recom[['Title', 'RecommendedScore']][recom['RecommendedScore'].notnull()])
    print()

    if save_output:
        print("Saving calculated rating recommendations to csv...")
        save_rating_recommendations(recom)

def save_rating_recommendations(recom):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"ratings_alg1_{timestamp}.csv"
    output_dir = Path("./data/out")
    output_dir.mkdir(parents=True, exist_ok=True)
    outpath = output_dir / filename
    recom.to_csv(outpath, index=False)
    print("Rating recommendations saved to csv.\n")

def print_user_evaluation_results_report(result, save_output = False):
    result["FinalScore"] = result["RecommendedScore"] + result["Notes"].astype(float).fillna(0).astype(int)


    print(result.sort_values(by="RecommendedScore", ascending=False)[["Title", "RecommendedScore", "FinalScore"]])
    print()

    print(f"User evaluation result: {(result["Accepted"].sum()/result.shape[0])*100}% accepted rating\n")

    if save_output:
        print("Saving user evaluation report to csv...")
        save_user_evaluation_results_report(result)

def save_user_evaluation_results_report(result):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"ratings_alg1_usereval_{timestamp}.csv"
    output_dir = Path("./data/out")
    output_dir.mkdir(parents=True, exist_ok=True)
    outpath = output_dir / filename
    result.to_csv(outpath, index=False)
    print("User evaluation report saved to csv.\n")