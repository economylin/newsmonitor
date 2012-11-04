PROJECT_WORKSPACE="$HOME/workspace-gae/newsmonitor"
export PYTHONPATH="$HOME/bin/google_appengine:$PYTHONPATH"
export PYTHONPATH="$PROJECT_WORKSPACE/src/library:$PYTHONPATH"
export PYTHONPATH="$PROJECT_WORKSPACE/src:$PYTHONPATH"
python "$PROJECT_WORKSPACE/test/unit/testcontentparser/testcontentparser.py"

