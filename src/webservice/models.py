from configmanager import cmapi

def _getKeyname():
    return 'source.deprecated'

def isSourceDeprecated(slug):
    return slug in cmapi.getItemValue(_getKeyname(), [],
                    modelname='RunStatus')

def removeDeprecatedSource(slug):
    items = cmapi.getItemValue(_getKeyname(), [],
                    modelname='RunStatus')
    if slug in items:
        items.remove(slug)
        cmapi.saveItem(_getKeyname(), items,
                modelname='RunStatus')

def addDeprecatedSource(slug):
    items = cmapi.getItemValue(_getKeyname(), [],
                    modelname='RunStatus')
    if slug not in items:
        items.append(slug)
        cmapi.saveItem(_getKeyname(), items,
                modelname='RunStatus')

