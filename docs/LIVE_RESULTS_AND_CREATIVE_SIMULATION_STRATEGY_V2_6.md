# Live Results and Creative Simulation Strategy V2.6

Real results are now necessary because the release candidate has moved from
pre-tournament prediction into observable tournament time. The product should
show what happened, score what the engine said beforehand, and update scenario
probabilities without pretending the earlier prediction knew the result.

**Never update a pre-match prediction after the match result is known. Add the
actual result as a separate evaluation layer.**

V2.6 therefore publishes results, per-match evaluation and conditioned
simulation as separate artifacts. Finished official scores can be locked in
the group simulation; live scores remain visible but are not treated as final.
Cards use one compact status/evaluation line, while the modal carries the
honest prediction-versus-reality detail.

Success language stays factual: exact score, Top-3, correct 1X2, protected DNB
or miss. It neither humiliates the model nor hides errors. Global conclusions
remain blocked while the finished sample is small.

The simulation page adds movement versus V2.4 and a creative campaign view.
Because current fixture data contains no official knockout mapping, the
campaign is a clearly labelled contender proxy. No opponent, final or bracket
is invented.
