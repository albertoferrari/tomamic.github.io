#!/usr/bin/env python3

import codecs
import re
import jinja2
import markdown
import os
import sys
import shutil
import time

#mic
def process_slides(inpath, outpath):
    with codecs.open(outpath, 'w', encoding='utf8') as outfile:
        md = codecs.open(inpath, encoding='utf8').read()
        md_slides = md.split('\n---\n')
        print('Compiled {} slides in {}.'.format(len(md_slides), inpath))
        # mic
        main_title = ''
        main_subtitle = ''
        main_figure = ''

        slides = []
        # Process each slide separately.
        for md_slide in md_slides:
            slide = {}
            sections = md_slide.split('\n\n')
            # Extract metadata at the beginning of the slide
            # (look for key: value) pairs.
            metadata_section = sections[0]
            metadata = parse_metadata(metadata_section)

            # mic
            if 'figure' in metadata:
                #metadata['figure'] = metadata['figure'].replace("images/", "https://raw.githubusercontent.com/tomamic/images/master/")
                #metadata['figure'] = metadata['figure'].replace(".svg", ".svg?sanitize=true")
                figure_parts = '!'.split(metadata['figure'], 2)
                metadata['figure_images'] = ' '.split(figure_parts[0])
                if len(figure_parts) == 2:
                    metadata['figure_caption'] = figure_parts[1]
            if main_title == '' and 'title' in metadata:
                main_title = metadata['title']
                if 'subtitle' in metadata:
                    main_subtitle = metadata['subtitle']
                if 'figure' in metadata:
                    main_figure = metadata['figure']
                continue
            if 'class' in metadata and 'break' in metadata['class']:
                break

            slide.update(metadata)
            remainder_index = metadata and 1 or 0
            # Get the content from the rest of the slide.
            content_section = '\n\n'.join(sections[remainder_index:])
            html = markdown.markdown(content_section, extensions=['tables'])
            slide['content'] = postprocess_html(html, metadata)

            slides.append(slide)

        template = jinja2.Template(open('theme/base.html').read())

        outfile.write(template.render(locals()))

def parse_metadata(section):
    """Given the first part of a slide, returns metadata associated with it."""
    metadata = {}
    metadata_lines = section.split('\n')
    for line in metadata_lines:
        colon_index = line.find(':')
        if colon_index != -1:
            key = line[:colon_index].strip()
            val = line[colon_index + 1:].strip()
            metadata[key] = val

    return metadata

def postprocess_html(html, metadata):
    """Returns processed HTML to fit into the slide template format."""
    html = re.sub(r"<p>code: *(py|c|c\+\+|cpp|java|js|html|css|hs|go|rs) *</p>\s*<pre>",
                  r'<pre class="prettyprint lang-\1" data-lang="\1">', html)
    html = re.sub(r"<p>code: *([^\n\r]*)</p>\s*<pre>",
                  r'<pre class="" data-lang="\1">', html)
    html = re.sub(r"\~\~([^\~]+)\~\~", r'<sub>\1</sub>', html)
    html = re.sub(r"\^\^([^\^]+)\^\^", r'<sup>\1</sup>', html)
    ## html = re.sub(r"<img([^>]+)svg", r'<embed\1svg', html)
    if metadata.get('build_lists') and metadata['build_lists'] == 'true':
        html = html.replace('<ul>', '<ul class="build">')
        html = html.replace('<ol>', '<ol class="build">')
    #html = html.replace("src=\"images/", "src=\"https://raw.githubusercontent.com/tomamic/images/master/")
    #html = html.replace(".svg\"", ".svg?sanitize=true\"")
    return html

if __name__ == '__main__':
    while True:
        for filename in os.listdir('mdp'):
            inpath = 'mdp/' + filename
            outpath = filename[:-4] + '.html'
            if filename.endswith(".mdp") and (not os.path.isfile(outpath) or
                os.path.getmtime(outpath) < os.path.getmtime(inpath)):
                process_slides(inpath, outpath)
        period = 5
        if len(sys.argv) > 1:
            period = int(sys.argv[1])
        if period > 0:
            time.sleep(period)
        else:
            sys.exit()
