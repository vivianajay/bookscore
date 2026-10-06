import pandas as pd
import numpy as np

OBJECTIVE_WEIGHT = 0.35
ENJOYMENT_WEIGHT = 0.65

def recomm_goodreads_rating(books):
    """
        Compute a Goodreads-style rating (1 to 5) for each book.

        Recommended Score = Base Rating + Experience Adjustment

            1. Base rating: book quality, based on two given ratings:
            - PersonalScore (more subjective enjoyment)
            - Rating (more objective evaluation)

            2. Reading experience adjustment, taking into account:
            - Ease of reading, normalized within each language
            - Reading speed, normalized against the reader's typical pace
              (using separate baselines for normal periods and reading slumps)

        Method
        ------
        1. Calculate a weighted average of the subjective and objective ratings.
        The subjective score has a larger weight.

        2. Calculate a language-adjusted ease coefficient.
        Ease scores are standardized (z-score) for each language, to account
        for differences in reading proficiency. Only books that are harder than
        average receive a small penalty; easier books do not get a bonus.

        3. Calculate a reading-speed coefficient.
        Reading speed is compared against the median speed for the corresponding
        context (normal reading or reading slump). "Faster than expected" books
        receive a small bonus, while slower books receive a small penalty.
        During reading slumps, this adjustment is further reduced because speed
        is considered a less reliable indicator of engagement.

        4. Sum the base score and the two adjustments.

        5. Round to the nearest integer and clip the result to the Goodreads
        1 to 5 rating scale.

        Returns
        -------
        pandas.DataFrame
        
            A DataFrame containing one row per book with the following columns:

            - Title (str): title of the book
            - AvgScore (float): weighted average of the subjective and objective ratings
            - EaseCoeff (float): ease-based penalty
            - SpeedCoeff (float): speed-based penalty or bonus
            - BeforeRounding (float): the recommended rating before rounding
            - RecommendedScore (nullable int): the final recommended Goodreads rating
    """
    
    base = (
        ENJOYMENT_WEIGHT * books["PersonalScore"] +
        OBJECTIVE_WEIGHT * books["Rating"] / 2 
    )

    # language-adjusted ease coefficient -
    # standardize EaseReading within each language and penalize only books
    # that are harder than the language average
    ease_z = (
        books["EaseReading"]
        - books.groupby("Language")["EaseReading"].transform("mean")
    ) / books.groupby("Language")["EaseReading"].transform("std").fillna(0)

    ease_adj = -np.clip(
        np.maximum(0, -ease_z) * 0.20,
        0,
        0.20,
    )

    # speed coefficient -
    # compare reading speed against the median speed for the corresponding
    # reading context (normal vs slump)
    median_normal = books.loc[~books["ReadingSlump"], "ReadingSpeed"].median()

    median_slump = books.loc[books["ReadingSlump"], "ReadingSpeed"].median()

    speed_baseline = np.where(
        books["ReadingSlump"],
        median_slump,
        median_normal
    )

    speed_adj = np.clip(
        0.15 * np.log(books["ReadingSpeed"] / speed_baseline),
        -0.20,
        0.20,
    )

    # reading speed is a weaker indicator of engagement during slumps,
    # so its contribution is reduced
    speed_adj *= np.where(books["ReadingSlump"], 0.25, 1.0)

    recommend = np.clip(
        np.round(base + ease_adj + speed_adj),
        1,
        5,
    ).astype("Int64")

    recom = books[['Title']].copy()

    recom["RecommendedScore"] = recommend
    
    recom["AvgScore"] = base
    recom["BeforeRounding"] = np.clip(
        base + ease_adj + speed_adj,
        1,
        5,
    )
    recom["EaseCoeff"] = ease_adj
    recom["SpeedCoeff"] = speed_adj

    return recom

def recom_ratings_user_evaluation(books, recom_ratings):

    result = recom_ratings.join(books[['EaseReading', 'PersonalScore', 'Rating','ReadingSpeed', 'ReadingSlump']])
    
    result = result[::-1]
    # print(result) # print all books before asking for review

    result = result[
        ['Title', 'EaseReading', 'PersonalScore', 'Rating','ReadingSpeed', 
        'ReadingSlump', 'AvgScore', "EaseCoeff","SpeedCoeff", "BeforeRounding",'RecommendedScore']
            ].dropna(subset=["AvgScore"]) # dropping books without score
    
    accepted = pd.Series()
    notes = pd.Series()

    for row in result.itertuples():
        if (row.AvgScore != row.RecommendedScore):
            #####################
            ### printing a book summary for the user
            #####################
            print("=" * 80)
            print(f"Book:                  {row.Title}")
            print("-" * 80)

            print(f"Ease of reading:       {row.EaseReading}/5")
            print(f"Rating:                {row.Rating}/10")
            print(f"Personal Score:        {row.PersonalScore}/5")

            print()
            print(
                f"Reading Speed:         {row.ReadingSpeed} pages/day"
                f"{' (in a reading slump)' if row.ReadingSlump else ''}"
            )

            print()
            print(f"Base Score:            {row.AvgScore}")
            print(f"Ease Coefficient:      {row.EaseCoeff}")
            print(f"Speed Coefficient:     {row.SpeedCoeff}")
            print(f"Score (decimal):       {row.BeforeRounding}")

            print()
            print(f"Recommended Score:     {row.RecommendedScore}")
            print("=" * 80)
            #####################

            response = ""
            while response not in {"Y", "N"}:
                response = input(f'Do you agree with the suggested rating ({row.RecommendedScore}) for this book? Y/N: ').strip().upper()

            accepted.loc[row.Index] = response == "Y"
            if not accepted.loc[row.Index]:
                note = ""
                while note not in {"-1", "+1"}:
                    note = input("Should the rating be higher (+1) or lower (-1)? ")
                notes.loc[row.Index] = note

            print("=" * 80)
            print()
        else:
            accepted.loc[row.Index] = True

    result["Accepted"] = accepted
    result["Notes"] = notes

    return result