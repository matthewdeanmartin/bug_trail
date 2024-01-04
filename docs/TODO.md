# TODO

## Multithreading support
- sqlite can't be used from 2 different threads
- hide thread id if they're all the same (ie. app is single threaded)
- p.oneshot() to add info about the process

## Data enrichment
- ???

## BUG
- Calculating path to pygmentized /src/ folder is messed up
- picologging should be an optional install

## Filewatcher + incremental update
- detail can be updated incrementally
- if we track hashes, we can update source incrementally

## integrate with pydoc_fork?
- link to symbol docs (not guaranteed to work, symbol data incomplete in log table)

## Goto Source code Line feature
- Copy source to folder as pretty html
- Add link to source code line in the html