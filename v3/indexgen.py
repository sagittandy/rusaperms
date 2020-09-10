"""
Generate the index page.

This is mostly just copying boilerplate, except
that we need to fill in a base URL in case we
are linking from index.html to another server
(e.g., from the Google Sites page to the
maps in AWS)
"""
import jinja2
import sys
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Maybe add configparser later, and extract the states
# from that.  But for now, we'll just use the verbose
# and hand-build boilerplate.
#

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate the index page")
    parser.add_argument('url', help="Base URL for linked maps",
                        nargs="?", default="./")
    parser.add_argument('template', help="The template for index.html",
                        nargs="?", default="index.html"),
    parser.add_argument('output', help="The html file to write",
                        type=argparse.FileType('w'),
                        nargs="?", default=sys.stdout)
    args = parser.parse_args()
    urlbase = args.url
    if not urlbase.endswith("/"):
        urlbase = urlbase + "/"
    env = {  "urlbase": urlbase }
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

