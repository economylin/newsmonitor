PROJECT_WORKSPACE="$HOME/workspace-gae/newsmonitor"
export PYTHONPATH="$PROJECT_WORKSPACE/src:$PROJECT_WORKSPACE/src/library:$PYTHONPATH"
python "$PROJECT_WORKSPACE/test/unit/testcontentfetcher/testcontentfetcher.py"

