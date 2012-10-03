from configmanager import cmapi

_GLOBAL_CONFIG_KEY = 'globalconfig'

_DEFAULT_FETCH_TIMEOUT = 10

_USER_AGENT = {
    'ie': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
    'firefox': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
}

def _getGlobalConfig():
    return cmapi.getItemValue(_GLOBAL_CONFIG_KEY)

def getFetchTimeout():
    gobalconfig = _getGlobalConfig()
    if gobalconfig:
        return gobalconfig.get('fetchtimeout', _DEFAULT_FETCH_TIMEOUT)
    return _DEFAULT_FETCH_TIMEOUT

def getUserAgent(useragent):
    return _USER_AGENT.get(useragent, useragent) if useragent else None

