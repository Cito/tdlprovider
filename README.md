tdlprovider
===========

Server that can be used as a ToDoList task provider for PyCharm

Requirements:
-------------

* [Python](http://www.python.org/) (version >= 2.6)
* [PyCharm](http://www.jetbrains.com/pycharm/) (version >= 2.7)
* [ToDoList](http://www.codeproject.com/Articles/5371/) (version >= 6.7)

Usage:
-------

This Python script runs a simple server on a chosen port that can be queried from PyCharm to get the currently active tasks in ToDoList.

Run the server with

    python tdlprovider.py [TDLPATH] [PORT]

where `TDLPATH` is the path to the directory containing the ToDoList tasklist files and `PORT` is the server port.

If you don't want to see the process in the task bar, copy pythonw.exe to the directory with tdlprovider.py, rename it to tdlprovider.exe,
and create a link "ToDoList Provider" to tdlprovider.exe. Then add `tdlprovider.py [TDLPATH] [PORT]` to the link target. If you start the script via the "ToDoList Provider" link now, it will run in the background and can be easily identified as "tdlprovider.exe" in the Windows task manager if you want to stop it again. You can also add tdlprovider.exe as a user defined tool to ToDoList. Set "Path" as the path to tdlprovider.exe, set "Arguments" to `tdlprovider.py "$(folder)" 8089` and set "Icon" as the path to PyCharm.

Add the server in PyCharm under Project Settings - Tasks - Servers as a Generic server and configure it like this:

* General:
  * Server URL: http://localhost:8089
    (the port can be configured in the script or via command line)
  * Login Anonymously: Yes
  * User/Password: None
  * User HTTP Authentication: No
* Additional:
  * Login URL: None
  * Task List URL: `{serverUrl}/LIST?query={query}&count={count}`
    (replace `LIST` with the name of your ToDoList tasklist file; the path to the ToDoList tasks lists can be configured either in the script or via a command line parameter)
  * Response Type: XML
  * Task Pattern: `<TASK ID="({id}[^"]*)" TITLE="({summary}[^"]*)" />`

Copyright and License:
----------------------

Copyright (c) 2013 Christoph Zwerschke

This script is released under the Apache v2 License.