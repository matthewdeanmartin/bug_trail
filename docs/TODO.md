# TODO

## Packaging
- split up to base/non base for pipx install and tiny handler. DONE
- picologging should be an optional install

## Main Views
- hide thread id if they're all the same (ie. app is single threaded)

## Detail View
- give up on iterated layout

## Data enrichment
- Sys info - Mostly done! (Check for doubling?)
- venv info - Mostly done! Neet to fix doubling.
- psutils p.oneshot() to add info about the process?
- Hava data! now link to symbol docs/pydoc (not guaranteed to work, symbol data incomplete in log table)
- Have data! now read docstrings of symbol (eg. error) maybe docstr of others?
- Have data! capture and store locals
- Use data cards
    - basic log info card
    - exception info card (type/instances)
    - stack trace card (call stack/locals)
## BUG
- Calculating path to pygmentized /src/ folder is messed up

## Filewatcher + incremental update
- detail can be updated incrementally
- if we track hashes, we can update source incrementally
