# Planet SymPy

This repository contains the code for the [Planet SymPy](https://planet.sympy.org/) website, which aggregates blog posts from SymPy contributors.

## How to add your blog

If you are a SymPy contributor, you can have your blog on Planet SymPy. Blog content can be SymPy/SymEngine/SciPy/Python themed, English language and not liable to offend. If you have a general blog, you may want to set up a tag and subscribe the feed for that tag only to Planet SymPy.

To have your blog added:
- File an issue on this GitHub repository listing your name, GitHub handle (if you have one), RSS or Atom feed and what you do in SymPy.
- Attach a photo of your face for hackergotchi.

Alternatively, you can submit a pull request:
- Add your hackergotchi in `static/hackergotchi/`. A hackergotchi should be a photo of your face smaller than 80x80 pixels with a transparent background.
- At the end of the `config/config` file add your details:
```
feed 15m http://example.com/feeds/feed.sympy.xml
        define_name Your Name (yourgithubhandle)
        define_face hackergotchi/yourgithubhandle.jpg
        define_facewidth 80
        define_faceheight 80
```

## Development

To build the site locally, run:

```
python3 planet.py build
```

This requires Python 3 and the following libraries: `feedparser`, `requests`, and `schedule`.

## Deployment

The site is automatically updated every 6 hours using GitHub Actions. The workflow:

1. Builds a Docker image containing the necessary code and dependencies
2. Runs the site generator to fetch feeds and generate the HTML output
3. Pushes the generated files to the [planet.sympy.org](https://github.com/planet-sympy/planet.sympy.org) repository

You can check the status of the latest update by looking at the Actions tab in this repository.

## Usage

The `planet.py` script provides several commands:

- `python3 planet.py build` - Build the website locally
- `python3 planet.py deploy` - Build and deploy to GitHub Pages
- `python3 planet.py scheduler` - Run the deployment scheduler (used in Docker)

## Technical Details

The site uses a custom Python-based RSS aggregator that:
- Fetches and parses RSS/Atom feeds from contributor blogs
- Generates HTML output using configurable templates
- Provides RSS, FOAF, and OPML formats for syndication
- Supports concurrent feed fetching for performance
- Includes modern Bootstrap styling