#!/usr/bin/env python3

import os
import sys
import time
import datetime
import re
import hashlib
import logging
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import html
import json
import subprocess
import shutil
import argparse

import feedparser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("planet")

class Feed:
    def __init__(self, url, period=None, **kwargs):
        self.url = url
        self.period = period or "15m"
        self.last_updated = 0
        self.title = kwargs.get("title", url)
        self.link = kwargs.get("link", "")
        self.options = kwargs
        
    def __str__(self):
        return f"Feed({self.url}, {self.title})"
    
    def get_id(self):
        return self.options.get("id", re.sub(r'[^a-zA-Z0-9]', '', self.title))

    def get_face(self):
        return self.options.get("define_face", "")
    
    def get_name(self):
        return self.options.get("define_name", self.title)
    
    def get_face_dimensions(self):
        width = self.options.get("define_facewidth", 80)
        height = self.options.get("define_faceheight", 80)
        return width, height

class Article:
    def __init__(self, entry, feed):
        self.entry = entry
        self.feed = feed
        self.title = entry.get("title", "No title")
        self.link = entry.get("link", "")
        self.description = entry.get("description", entry.get("summary", ""))
        self.date = self._parse_date(entry)
        self.id = entry.get("id", self.link)
        self.added = time.time()
        
    def _parse_date(self, entry):
        if "published_parsed" in entry and entry.published_parsed:
            return time.mktime(entry.published_parsed)
        elif "updated_parsed" in entry and entry.updated_parsed:
            return time.mktime(entry.updated_parsed)
        return time.time()
    
    def get_hash(self):
        return hashlib.md5(self.id.encode('utf-8')).hexdigest()
    
    def __str__(self):
        return f"Article({self.title}, {self.link})"

class PlanetAggregator:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config")
        self.feeds = []
        self.articles = []
        self.templates = {}
        self.config = {}
        self.read_config()
        
    def read_config(self):
        """Read the planet config file"""
        logger.info(f"Reading config from {self.config_file}")
        
        # Default config values
        self.config = {
            "maxarticles": 30,
            "maxage": 0,
            "daysections": True,
            "datetimeformat": "%H:%M, %A, %d %B",
            "dayformat": "%B %d, %Y",
            "outputfile": "index.html",
            "showfeeds": True,
            "sortbyfeeddate": True,
            "template": "planet_template",
            "itemtemplate": "itemplate",
            "outputxml": "rss10.xml",
            "outputxml2": "rss20.xml",
            "outputfoaf": "foafroll.xml",
            "outputopml": "opml.xml",
            "xmlmaxarticles": 30,
            "numthreads": 3
        }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse feeds and their options
            in_feed = False
            current_feed = None
            feed_options = {}
            
            for line in content.splitlines():
                orig_line = line
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check for config options
                if line.startswith('feed '):
                    if in_feed and current_feed:
                        self.feeds.append(Feed(current_feed, **feed_options))
                    
                    in_feed = True
                    parts = line[5:].split()
                    period = parts[0]
                    url = parts[1]
                    current_feed = url
                    feed_options = {'period': period}
                    
                    # Check for key=value arguments
                    for arg in parts[2:]:
                        if '=' in arg:
                            key, value = arg.split('=', 1)
                            feed_options[key] = value
                
                elif in_feed and orig_line.startswith(' ') and line.strip():
                    # Feed option on a new line
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                    else:
                        # Handle space-separated format like "define_name Timo Stienstra"
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            key, value = parts
                        else:
                            continue
                    feed_options[key] = value
                
                elif ' ' in line and not in_feed:
                    # Config option
                    key, value = line.split(' ', 1)
                    
                    # Convert numeric values
                    if key in ['maxarticles', 'maxage', 'xmlmaxarticles', 'numthreads']:
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                    
                    # Convert boolean values
                    elif value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    
                    self.config[key] = value
            
            # Add the last feed
            if in_feed and current_feed:
                self.feeds.append(Feed(current_feed, **feed_options))
            
            # Read template files
            template_file = self.config.get('template', 'planet_template')
            itemtemplate_file = self.config.get('itemtemplate', 'itemplate')
            
            self.templates['template'] = self._read_template(template_file)
            self.templates['itemtemplate'] = self._read_template(itemtemplate_file)
            
            logger.info(f"Loaded {len(self.feeds)} feeds from config")
            
        except Exception as e:
            logger.error(f"Error reading config: {e}")
            raise
    
    def _read_template(self, template_name):
        """Read a template file from the config directory"""
        template_path = os.path.join(self.config_dir, template_name)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading template {template_name}: {e}")
            return ""
    
    def fetch_feed(self, feed):
        """Fetch a single feed"""
        logger.info(f"Fetching feed: {feed.url}")
        try:
            data = feedparser.parse(feed.url)
            
            if data.get('bozo', 0) == 1:
                logger.warning(f"Feed {feed.url} seems malformed: {data.get('bozo_exception')}")
            
            # Update feed info
            if 'feed' in data and 'title' in data.feed:
                feed.title = data.feed.title
            if 'feed' in data and 'link' in data.feed:
                feed.link = data.feed.link
            
            # Process entries
            new_articles = []
            for entry in data.get('entries', []):
                article = Article(entry, feed)
                self.articles.append(article)
                new_articles.append(article)
            
            feed.last_updated = time.time()
            logger.info(f"Found {len(new_articles)} articles in {feed.url}")
            
            return new_articles
        except Exception as e:
            logger.error(f"Error fetching feed {feed.url}: {e}")
            return []
    
    def update(self):
        """Fetch all feeds in parallel"""
        logger.info(f"Updating {len(self.feeds)} feeds")
        
        max_workers = min(self.config.get('numthreads', 3), len(self.feeds))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            all_new_articles = list(executor.map(self.fetch_feed, self.feeds))
        
        # Flatten the list of articles
        new_articles = [article for sublist in all_new_articles for article in sublist]
        
        # Sort articles
        self._sort_articles()
        
        logger.info(f"Found {len(new_articles)} new articles across all feeds")
        return new_articles
    
    def _sort_articles(self):
        """Sort articles by date"""
        if self.config.get('sortbyfeeddate', True):
            self.articles.sort(key=lambda x: x.date, reverse=True)
        else:
            self.articles.sort(key=lambda x: x.added, reverse=True)
    
    def write(self, output_dir="build"):
        """Generate and write the output HTML file"""
        logger.info("Generating HTML output")
        
        self._sort_articles()
        
        # Limit the number of articles
        max_articles = self.config.get('maxarticles', 30)
        articles_to_show = self.articles[:max_articles] if max_articles > 0 else self.articles
        
        # Group articles by day if needed
        if self.config.get('daysections', True):
            grouped_articles = self._group_by_day(articles_to_show)
        else:
            grouped_articles = {'': articles_to_show}
        
        # Generate HTML for each article
        items_html = []
        for day, day_articles in grouped_articles.items():
            if day:
                items_html.append(f"<h2 class='date'>{day}</h2>")
            
            for article in day_articles:
                items_html.append(self._format_article(article))
        
        # Generate HTML for each feed
        feeds_html = []
        if self.config.get('showfeeds', True):
            for feed in self.feeds:
                face_html = ""
                if feed.get_face():
                    width, height = feed.get_face_dimensions()
                    face_html = f"<img class='face' src='{feed.get_face()}' width='{width}' height='{height}' alt='' />"
                
                feeds_html.append(
                    f"<li>{face_html}<a href='{feed.link}'>{feed.get_name()}</a></li>"
                )
        
        # Fill in the main template
        output = self.templates['template']
        output = output.replace('__version__', 'Planet SymPy 2.0')
        output = output.replace('__items__', '\n'.join(items_html))
        output = output.replace('__num_items__', str(len(articles_to_show)))
        output = output.replace('__feeds__', '<ul>\n' + '\n'.join(feeds_html) + '\n</ul>' if feeds_html else '')
        output = output.replace('__num_feeds__', str(len(self.feeds)))
        
        # Generate refresh meta tag if needed
        if self.config.get('userefresh', True):
            refresh_time = 60  # Default to 60 minutes
            output = output.replace('__refresh__', 
                f'<meta http-equiv="refresh" content="{refresh_time * 60}" />')
        else:
            output = output.replace('__refresh__', '')
            
        # Add RSS links
        output = output.replace('__rss10__', 'rss10.xml')
        output = output.replace('__rss20__', 'rss20.xml')
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Write the output to file
        output_file = self.config.get('outputfile', 'index.html')
        output_path = os.path.join(output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        
        logger.info(f"Wrote HTML output to {output_path}")
        
        # Generate RSS, FOAF and OPML
        self._write_xml_output(output_dir)
        
        return output_path
    
    def _format_article(self, article):
        """Format a single article using the item template"""
        output = self.templates['itemtemplate']
        
        feed = article.feed
        
        # Replace variables in the template
        output = output.replace('__title__', f"<a href='{article.link}'>{article.title}</a>" if article.link else article.title)
        output = output.replace('__title_no_link__', article.title)
        output = output.replace('__url__', article.link)
        output = output.replace('__guid__', article.id)
        output = output.replace('__description__', article.description)
        
        # Format dates
        dt_format = self.config.get('datetimeformat', '%H:%M, %A, %d %B')
        article_date = datetime.datetime.fromtimestamp(article.date)
        output = output.replace('__date__', article_date.strftime(dt_format))
        
        added_date = datetime.datetime.fromtimestamp(article.added)
        output = output.replace('__added__', added_date.strftime(dt_format))
        
        # Article hash
        output = output.replace('__hash__', article.get_hash())
        
        # Feed information
        output = output.replace('__feed_title__', f"<a href='{feed.link}'>{feed.title}</a>" if feed.link else feed.title)
        output = output.replace('__feed_title_no_link__', feed.title)
        output = output.replace('__feed_url__', feed.url)
        output = output.replace('__feed_hash__', hashlib.md5(feed.url.encode('utf-8')).hexdigest())
        output = output.replace('__feed_id__', feed.get_id())
        
        # Replace any custom feed definitions
        for key, value in feed.options.items():
            if key.startswith('define_'):
                var_name = key[7:]  # Remove 'define_' prefix
                output = output.replace(f'__{var_name}__', str(value))
        
        # Process conditionals like __if_description__
        face_value = feed.get_face()
        output = self._process_conditionals(output, {
            'title': article.title,
            'url': article.link,
            'guid': article.id,
            'description': article.description,
            'feed_title': feed.title,
            'feed_url': feed.url,
            'face': face_value
        })
        
        return output
    
    def _process_conditionals(self, template, values):
        """Process __if_*__ conditionals in templates"""
        for key, value in values.items():
            if f'__if_{key}__' in template:
                if value:
                    # Replace the conditional with its content
                    pattern = f'__if_{key}__(.*?)__endif__'
                    template = re.sub(pattern, r'\1', template, flags=re.DOTALL)
                else:
                    # Remove the conditional and its content
                    pattern = f'__if_{key}__.*?__endif__'
                    template = re.sub(pattern, '', template, flags=re.DOTALL)
        
        # Clean up any remaining conditionals
        template = re.sub(r'__if_.*?__.*?__endif__', '', template, flags=re.DOTALL)
        
        return template
    
    def _group_by_day(self, articles):
        """Group articles by day"""
        grouped = {}
        
        day_format = self.config.get('dayformat', '%B %d, %Y')
        
        for article in articles:
            day = datetime.datetime.fromtimestamp(article.date).strftime(day_format)
            if day not in grouped:
                grouped[day] = []
            grouped[day].append(article)
        
        # Return in reverse chronological order
        return {k: grouped[k] for k in sorted(grouped.keys(), reverse=True)}
    
    def _write_xml_output(self, output_dir):
        """Generate XML output files (RSS, FOAF, OPML)"""
        # Generate RSS 1.0
        if 'outputxml' in self.config:
            self._write_rss(self.config.get('outputxml'), output_dir)
        
        # Generate RSS 2.0
        if 'outputxml2' in self.config:
            self._write_rss2(self.config.get('outputxml2'), output_dir)
        
        # Generate FOAF
        if 'outputfoaf' in self.config:
            self._write_foaf(output_dir)
        
        # Generate OPML
        if 'outputopml' in self.config:
            self._write_opml(output_dir)
    
    def _write_rss(self, output_file, output_dir):
        """Generate RSS 2.0 output"""
        max_articles = self.config.get('xmlmaxarticles', 30)
        
        articles_to_show = self.articles[:max_articles] if max_articles > 0 else self.articles
        
        rss = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            '  <channel>',
            '    <title>Planet SymPy</title>',
            '    <link>https://planet.sympy.org/</link>',
            '    <description>Planet SymPy - https://planet.sympy.org/</description>',
            '    <atom:link href="https://planet.sympy.org/rss20.xml" rel="self" type="application/rss+xml" />',
            '    <language>en</language>',
            f'    <pubDate>{datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>',
        ]
        
        for article in articles_to_show:
            pub_date = datetime.datetime.fromtimestamp(article.date).strftime("%a, %d %b %Y %H:%M:%S +0000")
            
            rss.append('    <item>')
            rss.append(f'      <title>{html.escape(article.title)}</title>')
            rss.append(f'      <link>{html.escape(article.link)}</link>')
            rss.append(f'      <guid isPermaLink="false">{html.escape(article.id)}</guid>')
            rss.append(f'      <pubDate>{pub_date}</pubDate>')
            rss.append(f'      <description>{html.escape(article.description)}</description>')
            rss.append(f'      <source url="{html.escape(article.feed.url)}">{html.escape(article.feed.title)}</source>')
            rss.append('    </item>')
        
        rss.append('  </channel>')
        rss.append('</rss>')
        
        output_path = os.path.join(output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(rss))
        
        logger.info(f"Wrote RSS output to {output_path}")
    
    def _write_rss2(self, output_file, output_dir):
        """Generate RSS 2.0 output (same as RSS 1.0 for now)"""
        self._write_rss(output_file, output_dir)
    
    def _write_foaf(self, output_dir):
        """Generate FOAF output"""
        output_file = self.config.get('outputfoaf', 'foafroll.xml')
        
        foaf = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<rdf:RDF',
            '    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
            '    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"',
            '    xmlns:foaf="http://xmlns.com/foaf/0.1/"',
            '    xmlns:admin="http://webns.net/mvcb/"',
            '>',
            '  <foaf:Group>',
            '    <foaf:name>Planet SymPy</foaf:name>',
            '    <foaf:homepage rdf:resource="https://planet.sympy.org/" />',
            '    <admin:generatorAgent rdf:resource="https://github.com/sympy/planet-sympy" />',
        ]
        
        for feed in self.feeds:
            foaf.append('    <foaf:member>')
            foaf.append('      <foaf:Person>')
            foaf.append(f'        <foaf:name>{html.escape(feed.get_name())}</foaf:name>')
            if feed.link:
                foaf.append(f'        <foaf:weblog rdf:resource="{html.escape(feed.link)}" />')
            foaf.append('      </foaf:Person>')
            foaf.append('    </foaf:member>')
        
        foaf.append('  </foaf:Group>')
        foaf.append('</rdf:RDF>')
        
        output_path = os.path.join(output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(foaf))
        
        logger.info(f"Wrote FOAF output to {output_path}")
    
    def _write_opml(self, output_dir):
        """Generate OPML output"""
        output_file = self.config.get('outputopml', 'opml.xml')
        
        opml = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<opml version="1.1">',
            '  <head>',
            '    <title>Planet SymPy</title>',
            '  </head>',
            '  <body>',
        ]
        
        for feed in self.feeds:
            opml.append(f'    <outline text="{html.escape(feed.get_name())}" '
                       f'title="{html.escape(feed.title)}" '
                       f'type="rss" '
                       f'xmlUrl="{html.escape(feed.url)}" '
                       f'htmlUrl="{html.escape(feed.link)}" />')
        
        opml.append('  </body>')
        opml.append('</opml>')
        
        output_path = os.path.join(output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(opml))
        
        logger.info(f"Wrote OPML output to {output_path}")

def build_site(output_dir="build"):
    """Build the complete site"""
    logger.info("Building Planet SymPy site")
    
    # Clean any previous build
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create necessary directories
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "hackergotchi"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "js"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "fonts"), exist_ok=True)
    
    # Copy static resources
    static_dir = "static"
    if os.path.exists(static_dir):
        for item in os.listdir(static_dir):
            src = os.path.join(static_dir, item)
            dst = os.path.join(output_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        logger.info("Copied static resources")
    
    # Initialize and run the aggregator
    aggregator = PlanetAggregator("config")
    aggregator.update()
    aggregator.write(output_dir)
    
    logger.info(f"Build completed: website files are in {output_dir}/")

def deploy_site():
    """Deploy the site to GitHub Pages"""
    logger.info("Deploying Planet SymPy site")
    
    # Build first
    build_site()
    
    # Determine if this is testing or production
    testing = os.environ.get("TESTING") == "true"
    repo_suffix = "-test" if testing else ""
    
    # Clone the target repository
    subprocess.run([
        "git", "clone", 
        f"https://github.com/planet-sympy/planet.sympy.org{repo_suffix}"
    ], check=True)
    
    os.chdir(f"planet.sympy.org{repo_suffix}")
    
    # Configure git
    subprocess.run(["git", "config", "user.name", "Planet SymPy Bot"], check=True)
    subprocess.run(["git", "config", "user.email", "noreply@sympy.org"], check=True)
    
    commit_message = f"Publishing site on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Switch to gh-pages branch
    try:
        subprocess.run(["git", "checkout", "-t", "origin/gh-pages"], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "checkout", "gh-pages"], check=True)
    
    # Remove existing files and copy new ones
    for item in os.listdir("."):
        if item != ".git":
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
    
    # Copy built files
    for item in os.listdir("../build"):
        src = os.path.join("../build", item)
        if os.path.isdir(src):
            shutil.copytree(src, item)
        else:
            shutil.copy2(src, item)
    
    # Add CNAME file for production
    if not testing:
        with open("CNAME", "w") as f:
            f.write("planet.sympy.org\n")
    
    # Add .nojekyll file
    with open(".nojekyll", "w") as f:
        f.write("")
    
    # Commit changes
    subprocess.run(["git", "add", "-A", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    
    logger.info("Deploying:")
    
    # Check if we have SSH key for deployment
    if not os.environ.get("SSH_PRIVATE_KEY"):
        logger.info("Not deploying because SSH_PRIVATE_KEY is empty.")
        return
    
    # Push to GitHub
    subprocess.run(["git", "push", "origin", "gh-pages"], check=True)
    logger.info("Deployment completed")

def run_scheduler():
    """Run the deployment scheduler"""
    import schedule
    
    logger.info("Starting Planet SymPy scheduler")
    logger.info("Docker environment variables:")
    
    if os.environ.get("SSH_PRIVATE_KEY"):
        logger.info("SSH_PRIVATE_KEY = <non-empty ssh private key>")
    else:
        logger.info("SSH_PRIVATE_KEY = <empty>")
    
    logger.info(f"TESTING = {os.environ.get('TESTING')}")
    
    # Schedule deployment every 6 hours
    schedule.every(6).hours.do(deploy_site)
    
    # Run initial deployment
    try:
        deploy_site()
    except Exception as e:
        logger.error(f"Initial deployment failed: {e}")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def main():
    parser = argparse.ArgumentParser(description="Planet SymPy - RSS/Atom feed aggregator")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build the website')
    build_parser.add_argument('--output-dir', default='build', help='Output directory (default: build)')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy the website to GitHub Pages')
    
    # Scheduler command
    scheduler_parser = subparsers.add_parser('scheduler', help='Run the deployment scheduler')
    
    # Legacy rawdog-style arguments for backwards compatibility
    parser.add_argument('-d', '--config-dir', default='config', help='Configuration directory')
    parser.add_argument('--update', action='store_true', help='Update feeds')
    parser.add_argument('--write', action='store_true', help='Write output files')
    parser.add_argument('--output-dir', default='build', help='Output directory')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        build_site(args.output_dir)
    elif args.command == 'deploy':
        deploy_site()
    elif args.command == 'scheduler':
        run_scheduler()
    elif args.update or args.write:
        # Legacy mode for backwards compatibility
        aggregator = PlanetAggregator(args.config_dir)
        
        if args.update:
            aggregator.update()
        
        if args.write:
            aggregator.write(args.output_dir)
    else:
        # Default: build the site
        build_site()

if __name__ == "__main__":
    main()