# Plan: textkit string helpers

## Task 1: slugify
Add `slugify(text)` to `textkit/slug.py`: lowercase, non-alphanumerics become single hyphens, trim hyphens. Add tests in `tests/test_slug.py`.

## Task 2: truncate
Add `truncate(text, limit)` to `textkit/trim.py`: cut to `limit` chars and append "..." if cut. Add tests in `tests/test_trim.py`.

## Task 3: word_count
Add `word_count(text)` to `textkit/count.py`: number of whitespace-separated words. Add tests in `tests/test_count.py`.
