#!/usr/bin/env python

"""Server that can be used as a ToDoList task provider for PyCharm

Requirements:

    Python: http://www.python.org/ (version >= 2.6)
    PyCharm: http://www.jetbrains.com/pycharm/ (version >= 2.7)
    ToDoList: http://www.codeproject.com/Articles/5371/ (version >= 6.7)

This Python script runs a simple server on a chosen port that can be
queried from PyCharm to get the currently active tasks in ToDoList.

Run the server with: python tdlprovider.py [TDLPATH] [PORT]

    where TDLPATH is the path to the directory containing
    the ToDoList tasklist files and PORT is the server port

Add the server in PyCharm under Project Settings - Tasks - Servers
as a Generic server and configure it like this:

    General:

    Server URL: http://localhost:8089
      (the port can be configured in the script or via command line)
    Login Anonymously: Yes
    User/Password: None
    User HTTP Authentication: No

    Additional:

    Login URL: None
    Task List URL: {serverUrl}/LIST?query={query}&count={count}
      (replace LIST with the name of your ToDoList tasklist file;
       the path to the ToDoList tasks lists can be configured
       either in the script or via a command line parameter)
    Response Type: XML
    Task Pattern: <TASK ID="({id}[^"]*)" TITLE="({summary}[^"]*)" />

Copyright (c) 2013 Christoph Zwerschke

This script is released under the Apache v2 License.

"""

import os
import sys
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:  # Python < 3
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:  # Python < 3
    from urlparse import urlparse, parse_qs
from xml.sax.saxutils import quoteattr
try:
    import xml.etree.cElementTree as ET
except ImportError:  # Python >= 3.3
    from xml.etree import ElementTree as ET

PATH = r'C:\ToDoList\Resources\TaskLists'
PORT = 8089


def attr(text):
    """Escape and encode text as XML attribute."""
    return quoteattr(text).encode('utf-8')


class HTTPHandler(BaseHTTPRequestHandler):
    """Handler for ToDoList task server."""

    base_path = PATH

    def collect_tasks(self, tasklist, count, query, parsed):
        """Collect all tasks in given element list."""
        for task in tasklist:
            if task.tag == 'TASK':
                # do not show closed tasks
                if task.get('DONEDATE'):
                    continue
                task_id = task.get('ID')
                title = task.get('TITLE')
                # check how well query matches
                if query:
                    match = 0
                    for text in task_id, title:
                        if text:
                            text = text.lower()
                            if query in text:
                                match -= 1
                                if text.startswith(query):
                                    match -= 1
                                    if text == query:
                                        match -= 1
                else:
                    match = -1
                if match:
                    # get due date
                    try:
                        due = float(task.get('DUEDATE'))
                    except (TypeError, ValueError):
                        due = float('inf')
                    # get priority
                    try:
                        priority = -int(task.get('PRIORITY'))
                    except (TypeError, ValueError):
                        priority = 1
                    # order by match quality, due date, priority, id
                    parsed.append((match, due, priority, task_id, title))
                # collect all sub-tasks
                self.collect_tasks(task, count, query, parsed)
                # end if request limit reached
                if count and len(parsed) >= count:
                    break
        return parsed

    def get_tdl_tasks(self, tasklist, count, query):
        """Get all TodoList tasks from the tasklist file."""
        path = self.base_path
        if tasklist:
            path = os.path.join(path, tasklist)
        if not path.endswith('.tdl'):
            path += '.tdl'
        try:
            tasklist = ET.parse(path).getroot().getchildren()
        except IOError:
            print('Could not open {0}'.format(path))
            return
        except SyntaxError:
            print('Could not parse {0}'.format(path))
            return
        if query:
            query = query.lower()
        tasklist = self.collect_tasks(
            tasklist, 0 if query else count, query, [])
        # Sort result
        tasklist.sort()
        if count:
            tasklist = tasklist[:count]
        tasklist = [task[3:] for task in tasklist]
        return tasklist

    def do_GET(self):
        """Answer GET request."""
        parsed = urlparse(self.path)
        tasklist = parsed.path.strip('/')
        parsed = parse_qs(parsed.query)
        try:
            count = int(parsed.get('count')[0])
        except (ValueError, TypeError):
            count = None
        try:
            query = parsed.get('query')[0]
        except TypeError:
            query = None
        tasks = self.get_tdl_tasks(tasklist, count, query)
        if tasks is None:
            self.send_error(404, 'Task list not found')
            return
        self.send_response(200)
        self.send_header('Content-type', 'text/xml; charset=utf-8')
        self.end_headers()
        wf = self.wfile
        wr = wf.write
        wr(b'<?xml version="1.0" encoding="UTF-8" ?>\n')
        wr(b'<TASKLIST>\n')
        for task_id, title in tasks:
            wr(b'<TASK ID='
               + attr(task_id) + b' TITLE=' + attr(title) + b' />')
        wr(b'</TASKLIST>\n')


def main(path, port):
    """Run TodoList task server."""
    print('Serving ToDoList from {0} on port {1}...'.format(path, port))
    HTTPHandler.base_path = path
    server = HTTPServer(('localhost', port), HTTPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stop serving ToDoList...')
        server.socket.close()


if __name__ == "__main__":
    path = PATH
    port = PORT
    args = sys.argv[1:]
    if args:
        path = args[0]
        if len(args) > 1:
            port = int(args[1])
    main(path, port)
