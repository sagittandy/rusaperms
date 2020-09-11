"""
Generate the index page.

This is mostly just copying boilerplate, except
that we need to fill in a base URL in case we
are linking from index.html to another server
(e.g., from the Google Sites page to the
maps in AWS)
"""

import count_perms

import jinja2
import sys

import configparser
import argparse
CONFIG_FILE = "leafletmaps.config"

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Maybe add configparser later, and extract the states
# from that.  But for now, we'll just use the verbose
# and hand-build boilerplate.
#

def config():
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    return parser["DEFAULT"]

def cli() -> object:
    """Returns plain object with argument fields"""
    # Some defaults could come from config file
    defaults = config()
    parser = argparse.ArgumentParser(description="Generate the index page")
    parser.add_argument('--url_base', help="Base URL for linked maps",
                        nargs="?", default=defaults["url_base"])
    parser.add_argument('--template', help="The template for index.html",
                        nargs="?", default="index.html"),
    parser.add_argument('--output', help="The html file to write",
                        type=argparse.FileType('w'),
                        nargs="?", default=sys.stdout)
    args = parser.parse_args()
    return args

def main():
    args = cli()
    url_base = args.url_base
    if not url_base.endswith("/"):
        url_base = url_base + "/"
    regions = sorted(count_perms.perm_counts())
    env = {  "url_base": url_base, "regions": regions }
    template_loader = jinja2.FileSystemLoader(searchpath="templates" )
    template_env = jinja2.Environment(
        loader=template_loader,
        lstrip_blocks=True
        )
    template = template_env.get_template( args.template )
    output_text = template.render( env )
    print(output_text, file=args.output)
    
if __name__ == "__main__":
    main()

