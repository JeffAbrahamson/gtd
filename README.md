# gtd
Tools for analyzing my time usage.

## Programs

Quite a bit of common infrastructure lives in `lib_gtd.py`.

* `refresh.py` reads the raw data files and either creates or updates the database.  The database directory (~/.gtd_analysis/) must exist.
* `label_point.py` presents the user with (randomly selected) window names and contents and asks for labels.
* `status.py` reports on basic feature stats.
* `histogram_labels.py` provides a histogram of how many points are labeled and how.
* `rename_label.py` corrects labels (somewhat crudely: all of one label becomes another).
* `extract_features_tfidf.py` extracts tf-idf features from window titles and stores them in the gtd_data dict.
