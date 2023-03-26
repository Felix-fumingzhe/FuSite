# encoding = utf-8

import ybc_config
from ybc_commons import httpclient
# from urllib.request import urlretrieve
from ybc_commons.ArgumentChecker import Argument
from ybc_commons.ArgumentChecker import Checker
# from ybc_commons.util import Predicate
from ybc_commons.util.predicates import non_blank

_IDIOM_MEANING_URL_PATH = 'idiom-meaning'
_IDIOM_SEARCH_URL_PATH = 'idiom-search'
# _IDIOM_FIND_URL_PATH = 'idiom-find'
# _IDIOM_COMPARE_URL_PATH = 'idiom-compare'
# _HISTORY_QUERY_URL = 'history'
# _DEFAULT_EVENTS_NUMS = 3

# _XIAOHUA_URL = 'funny/joke'
# _RAOKOULING_URL = 'funny/tongue-twister'
# _JIZHUANWAN_CONTENT_URL = 'funny/brain-twister/content'
# _JIZHUANWAN_ANSWER_URL = 'funny/brain-twister/answer'
# _XIEHOUYU_CONTENT_URL = 'funny/allegory/content'
# _XIEHOUYU_ANSWER_URL = 'funny/allegory/answer'
# _RIDDLE_CONTENT_URL = 'funny/riddle/content'
# _RIDDLE_ANSWER_URL = 'funny/riddle/answer'
__PREFIX = ybc_config.config['course-api-prefix']
__ARTICLE_SEARCH_URL = __PREFIX + '/articles/search'

__POETRY_URL = 'poetry'


def _meaning(keyword: str):
    Checker.check_arguments(
        [Argument('ybc_txt_search', '_meaning', 'keyword', keyword, str, non_blank)])
    data = {'keyword': keyword}
    result = httpclient.post(_IDIOM_MEANING_URL_PATH, data)
    if result['code'] != 0:
        return -1
    return result['idiomMeaning']

def _search(keyword: str):
    Checker.check_arguments(
        [Argument('ybc_txt_search', '_search', 'keyword', keyword, str, non_blank)])
    data = {'keyword': keyword}
    result = httpclient.post(_IDIOM_SEARCH_URL_PATH, data)
    if result['code'] != 0 or len(result['idiomList']) < 1:
        return -1
    return result['idiomList']

def idiom(keyword: str):
    Checker.check_arguments(
        [Argument('ybc_txt_search', 'idiom', 'keyword', keyword, str, non_blank)])
    return _meaning(keyword)

def idiom_list(keyword: str):
    Checker.check_arguments(
        [Argument('ybc_txt_search', 'idiom_list', 'keyword', keyword, str, non_blank)])
    return _search(keyword)

def idiom_search(keyword):
    idiomList = []
    idiom_List = idiom_list(keyword)
    if idiom_List == -1:
        return None
    for idiom_txt in idiom_List:
        idiom_dict = {}
        idiom_dict_n = idiom(idiom_txt)
        if idiom_dict_n == -1:
            continue
        idiom_dict["名称"] = idiom_dict_n["名称"]
        idiom_dict["读音"] = idiom_dict_n["读音"]
        idiom_dict["解释"] = idiom_dict_n["解释"]
        idiom_dict["出自"] = idiom_dict_n["出自"]
        idiom_dict["同义词"] = ";".join(idiom_dict_n["同义词"])
        idiom_dict["反义词"] = ";".join(idiom_dict_n["反义词"])
        idiom_dict["举例"] = idiom_dict_n["举例"]
        idiomList.append(idiom_dict)
    if idiomList is not []:
        return idiomList
    else:
        return None

