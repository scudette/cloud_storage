#!/usr/bin/python
"""Makes an index.html of the bucket directory."""

import argparse
import re
import time
import os


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{bucket_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://code.jquery.com/jquery-1.11.0.min.js"></script>
    <script src="https://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>

    <script src="https://netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="https://code.jquery.com/ui/1.10.4/themes/smoothness/jquery-ui.css">
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">

</head>
<body>
<div class="container bs-docs-container">
<div class="row">
  <div class="col-md-10" role="main">
<h1>{bucket_name}</h1>
    {body}
  </div>
</div>
</div>
</body>
</html>
"""

def render_link(ignores, full_path, relative_path):
    for regex in ignores:
        if regex.match(relative_path):
            print "Ignoring %s" % relative_path
            return ""

    s = os.stat(full_path)

    return """
<tr>
  <td>{size}</td><td>{date}</td>
  <td>
    <a href='{relpath}'>{relpath}</a>
  </td>
</tr>""".format(relpath=relative_path,
                size=s.st_size, date=time.ctime(s.st_mtime))



def render_page(bucket_path):
    bucket_path = os.path.normpath(bucket_path)
    bucket_name = os.path.basename(bucket_path)
    try:
        header = open(os.path.join(bucket_name, "header.html")).read()
        header = header.format(bucket_name=bucket_name)
    except IOError:
        header = ""

    try:
        ignores = [re.compile(x) for x in (open(
            os.path.join(bucket_name, ".ignore")).read().splitlines())]
    except IOError:
        ignores = []


    body = """
<div class="panel panel-default">
  {header}
  <!-- Table -->
  <table class="table">
    <thead>
      <tr><th>Size</th><th>Date</th><th>File name</th></tr>
    </thead>
    <tbody>
""".format(header=header)

    bucket_path = os.path.normpath(os.path.abspath(bucket_path))

    for root, _, files in os.walk(bucket_path):
        for name in sorted(files):
            full_path = os.path.normpath(os.path.join(root, name))
            relative_path = os.path.relpath(full_path, bucket_path)
            body += render_link(ignores, full_path, relative_path)

    body += """
    </tbody>
  </table>
</div>
"""

    return TEMPLATE.format(bucket_name=bucket_name, body=body)


PARSER = argparse.ArgumentParser()
PARSER.add_argument("bucket_path",
                    help="The path to the gs directory.")

PARSER.add_argument("--output", default=None,
                    help="Write to this file instead.")

if __name__ == "__main__":
    FLAGS = PARSER.parse_args()

    page = render_page(bucket_path=FLAGS.bucket_path)
    output = FLAGS.output or os.path.join(FLAGS.bucket_path, "index.html")

    with open(output, "wb") as fd:
        fd.write(page)
