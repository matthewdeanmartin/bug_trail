# TODO

## Packaging
- split up to base/non base for pipx install and tiny handler
- picologging should be an optional install

## Main Views
- hide thread id if they're all the same (ie. app is single threaded)

## Detail View
- give up on iterated layout

## Data enrichment
- psutils p.oneshot() to add info about the process?
- link to symbol docs/pydoc (not guaranteed to work, symbol data incomplete in log table)
- read docstrings of symbol (eg. error)
- capture and store locals

## BUG
- Calculating path to pygmentized /src/ folder is messed up

## Filewatcher + incremental update
- detail can be updated incrementally
- if we track hashes, we can update source incrementally
