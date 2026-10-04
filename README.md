# BorderQueue site

Static site for BorderQueue: the queue at the Belarus–EU border right now, how long cars actually
waited, when to register on a weekend, and how accurate the forecast is. Russian-language.

- Pages are plain HTML, built from one template: `python tools/build.py`.
- Numbers come from the bot's public read-only endpoints at
  `https://borderqueueapi.onrender.com/api/public/{now,weekend,accuracy,totals}`. The bot service
  computes them in the background and serves them from memory, so the site never reaches the
  database. Source: the BorderQueue repository, `PublicStatsService.cs`.
- No build step and no dependencies: GitHub Pages serves the repository root as is.
- Links to the bot carry `?start=site…` labels so the bot can count visitors from each page.

To move to a custom domain, change `SITE` in `tools/build.py`, rebuild, and add a `CNAME` file.
