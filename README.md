> **Update-- 6th October 2026:** Goodreads has finally introduced half- and quarter-star ratings. This makes the original purpose of this project somewhat obsolete, but since I had fun building it, I'm keeping it here as a small personal data-analysis project.  
>
> ["The (Half) Stars Have Aligned"](https://www.goodreads.com/blog/show/3199?ref=hs_sb)

Goodreads doesn't allow "half-star" reviews. I needed something to help me figure out how to convert my decimal grades. No, just rounding up - or, more likely, rounding down - wasn't enough.

On a more serious note:

**input:**

- a CSV with data on recently read books (source: my Notion database, where I can freely and privately vent about the books I've read)

**output:**

- brief and simple data analysis of what I read and how I liked it
- whole-number ratings helper for Goodreads, with optional interactive user evaluation

Thanks to my infinite creativity, this 'project' was originally called *books-rating-helper-and-analyser*. Thanks (?) to ChatGPT, it is now named `bookscore`. I'm still not entirely convinced this was an upgrade.

---

DNF books are not currently supported. This wasn't really a design decision so much as a reflection of how I use my reading database: I rarely mark books as DNF, so I didn't have much data to build or test that part of the analysis around.

### Sample data

To allow the project to run without needing to access my actual reading database, the repository includes a small sample CSV file containing just a few records. It has the same columns and structure as the CSV file exported from my Notion.

### Usage

Run:

    python main.py

By default, this uses *./data/books.csv*. You can also provide a different CSV:

    python main.py path/to/books.csv


**Options**
|  |  |
|---|---|
| `--analysis-only` | only run the reading analysis |
| `--ratings-only` | only generate rating recommendations |
| `--user-evaluation` | interactively evaluate the recommended ratings |
| `--end-date YYYY-MM-DD` | only include books finished on or after the given date |
| `--save-output` | save reports and cleaned data to `./data/out` |
|  |  |


For example:

    python main.py --user-evaluation --save-output