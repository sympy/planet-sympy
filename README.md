# Planet SymPy

This repository contains the code for the [Planet SymPy](https://planet.sympy.org/) website, which aggregates blog posts from SymPy contributors.

## How to add your blog

If you are a SymPy contributor, you can have your blog on Planet SymPy. Blog content can be SymPy/SymEngine/SciPy/Python themed, English language and not liable to offend. If you have a general blog, you may want to set up a tag and subscribe the feed for that tag only to Planet SymPy.

To have your blog added, submit a pull request:
- Add your photo in `static/avatars/`. Avatar photos should be 80x80 pixels.
- Add your feed details to the `config/config.yaml` file:
```yaml
  - url: http://example.com/feeds/feed.sympy.xml
    name: Your Name (yourgithubhandle)
    face: yourgithubhandle.jpg
```

## Development

To build the site locally, run:

```
python3 planet.py build
```

This requires Python 3 and the following libraries: `feedparser`, `pyyaml`, and `requests`.

## Deployment

The site is automatically updated every 6 hours using GitHub Actions. The workflow:

1. Sets up Python environment and installs dependencies
2. Runs the site generator to fetch feeds and generate the HTML output
3. Deploys the generated files directly to GitHub Pages

You can check the status of the latest update by looking at the Actions tab in this repository.

## Usage

The `planet.py` script provides several commands:

- `python3 planet.py build` - Build the website locally
- `python3 planet.py deploy` - Build and deploy to GitHub Pages

## Technical Details

The site uses a custom Python-based RSS aggregator that:
- Fetches and parses RSS/Atom feeds from contributor blogs
- Generates HTML output using configurable templates
- Provides RSS, FOAF, and OPML formats for syndication
- Supports concurrent feed fetching for performance
- Includes modern Bootstrap styling
