# Minichess

This repo contains two implementations of a simple chess bot that plays a
smaller version of chess called Minichess, specifically the Minitchess variant.

The rules are similar to regular chess, with a few exceptions:

1. The game is won by king capture, rather than checkmate. There is no 'check'.

2. The bishop can move in the main cardinal directions one square but cannot
capture while doing so.

3. Pawns can only be promoted to queens.

Build instructions for each implementation can be found in their respective
subdirectories. 

The Java version was implemented second in an (successful) attempt to increase
performance. Due to time constraints, I relied on the unit tests written for 
the Python version to help ensure some small amount of certainty in correctness,
but Java tests may be added at a later date for completeness. The Java version
has therefore also been refactored slightly more than the Python version.
