"120" is a tabletop simulator for the 120-cell, a 4-dimensional polytope.

Just as the dodecahedron covers the sphere in 3 dimensions with 12 pentagons,
the 120-cell covers the hypersphere in 4 dimensions with 120 dodecahedra.

*See https://en.wikipedia.org/wiki/120-cell for more geometric details.

This seemed, vaguely, like a reasonable scale for a game board, with games
like chess and go played on boards from a few dozen to a few hundred spaces.

What games will actually work on the 120-cell remains to be discovered.

== how to use 120 ==

Each game will consist of its own Python file that builds on the core modules
of 120 -- you'll run a particular game, rather than "running 120".

For example, to run Halma:

> python halma.py

All games present the same view of the 120-cell, in which the view from the
camera is projected onto the screen via a Mercator projection, and the same
controls for shifting and rotating the camera view:

move: W, A, S, D, Shift, Control
rotate Up, Down, Left, Right, Q, E

Each game defines a set of players and a set of actions or verbs.
These in turn determine which locations or objects are clickable.

*Visual indication of the current player and verb will be added in the future.
*See individual readme files for each game program for how to play.

Move the mouse to highlight clickable locations under the cursor.
If multiple locations at different depths are highlighted, switch with Tab.
Click to perform the current action on the highlighted location.

Z to Undo
P to switch Players
V to switch Verbs (in games with more than one verb)

Close the window to exit.
