# gtd
Tools for analyzing my time usage.

## Programs

Quite a bit of common infrastructure lives in `lib_gtd.py`.

* `refresh.py` reads the raw data files and either creates or updates the database.  The database directory (~/.gtd_analysis/) must exist.
* `label_point.py` presents the user with (randomly selected) window names and contents and asks for labels.
