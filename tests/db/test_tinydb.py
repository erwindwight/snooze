#!/usr/bin/python3.6

from snooze.db.database import Database

import pytest
from pathlib import Path
from os import remove

from logging import getLogger
log = getLogger('snooze.test.tinydb')

from tinydb import TinyDB, Query

import yaml

with open('./examples/local_db.yaml', 'r') as f:
    default_config = yaml.load(f.read())

@pytest.fixture(scope='function')
def tinydb_file():
    filename = './db_test.json'
    Path(filename).touch()
    yield filename
    remove(filename)

@pytest.fixture
def db(tinydb_file):
    config = {'type': 'file', 'path': tinydb_file}
    return Database(config)

def test_tinydb_base(tinydb_file):
    db = TinyDB(tinydb_file)
    db.insert({'a': '1'})
    db.insert({'b': '2'})
    Records = Query()
    log.debug(db.all())
    log.debug(db.search(Records['a'] == '1'))
    log.debug(db.search(Records['b'] == '2'))
    assert True

def test_tinydb_all(db):
    db.write('record', {'a': '1', 'b': '2'})
    assert db.search('record')['data'][0].items() >= {'a': '1', 'b': '2'}.items()

def test_tinydb_search(db):
    db.write('record', [{'a': 1, 'b': 2, 'd': 1},{'a': 30, 'b': 40, 'c': 'tata', 'd': 1}])
    search1 = ['AND', ['=', 'a', 1], ['!=', 'b', 40]]
    result1 = db.search('record', search1)['count']
    search2 = ['OR', ['=', 'a', 1], ['=', 'a', 30]]
    result2 = db.search('record', search2)['count']
    search3 = ['MATCHES', 'c', 'ta*']
    result3 = db.search('record', search3)['count']
    search4 = ['NOT', ['=', 'a', 1]]
    result4 = db.search('record', search4)['count']
    search5 = ['EXISTS', 'c']
    result5 = db.search('record', search5)['count']
    search6 = ['>', 'a', 1]
    result6 = db.search('record', search6)['count']
    search7 = ['<', 'c', 'toto']
    result7 = db.search('record', search7)['count']
    search8 = ['=', 'c', 'toto']
    result8 = db.search('record', search8)['count']
    search9 = ['AND', ['=', 'b', 2], ['OR', ['=', 'd', 2], ['=', 'd', 1]]]
    result9 = db.search('record', search9)['count']
    assert result1 == 1
    assert result2 == 2
    assert result3 == 1
    assert result4 == 1
    assert result5 == 1
    assert result6 == 1
    assert result7 == 1
    assert result8 == 0
    assert result9 == 1

def test_tinydb_search_contains(db):
    db.write('record', [{'a': ['00', '11', '22']}, {'a': ['00', '1', '2']}, {'a': ['00', '1', '4']}, {'b': '5'}])
    result1 = db.search('record', ['CONTAINS', 'a', '1'])['data']
    result2 = db.search('record', ['CONTAINS', 'a', ['2', '4']])['data']
    result3 = db.search('record', ['CONTAINS', 'b', ['5', '1']])['data']
    assert len(result1) == 3 and len(result2) == 3 and len(result3) == 1

def test_tinydb_search_in(db):
    db.write('record', [{'a': ['00', '11', '22']}, {'a': ['00', '1', '2']}, {'a': ['00', '1', '4']}, {'b': '5'}])
    result1 = db.search('record', ['IN', '1', 'a'])['data']
    result2 = db.search('record', ['IN', ['2', '4'], 'a'])['data']
    result3 = db.search('record', ['IN', ['5', '1'], 'b'])['data']
    assert len(result1) == 2 and len(result2) == 2 and len(result3) == 1

def test_tinydb_search_in_query(db):
    db.write('record', [{'b': [{'x': '00'}, {'y':'1'}, {'z':'2'}]}, {'a': [{'x': '00'}, {'y':'1'}, {'z':'2'}]}, {'a': [{'x': '00'}, {'y':'1'}, {'z':'4'}]}])
    result1 = db.search('record', ['IN', ['=', 'y', '1'], 'b'])['data']
    result2 = db.search('record', ['IN', ['=', 'y', '1'], 'a'])['data']
    result3 = db.search('record', ['IN', ['OR', ['=', 'z', '2'], ['=', 'z', '4']], 'a'])['data']
    assert len(result1) == 1 and len(result2) == 2 and len(result3) == 2

def test_tinydb_search_text(db):
    db.write('record', [{'myfield': [{'found':'mystring'}, {'mysearch': '0'}]}, {'a': {'found': 'myvalue'}}])
    assert len(db.search('record', ['SEARCH', 'field'])['data']) == 1
    assert len(db.search('record', ['SEARCH', 'string'])['data']) == 1
    assert len(db.search('record', ['SEARCH', 'value'])['data']) == 1
    assert len(db.search('record', ['SEARCH', 'found'])['data']) == 2
    assert len(db.search('record', ['OR', ['SEARCH', 'string'], ['SEARCH', 'value']])['data']) == 2
    assert len(db.search('record', ['SEARCH', 'unknown'])['data']) == 0

def test_tinydb_search_nested(db):
   db.write('record', [{'a': [1, 2], 'b': {'c': 2, 'd': 3}}])
   assert len(db.search('record', ['=', 'b.c', 2])['data']) == 1
   assert len(db.search('record', ['=', 'a.1', 2])['data']) == 1

def test_tinydb_search_page(db):
    log.debug(db.search('record')['data'])
    db.write('record', [{'a': '1', 'b': '2'},{'a': '2', 'b': '2'},{'a': '3', 'b': '2'},{'a': '4', 'b': '2'},{'a': '5', 'b': '2'}])
    search = ['=', 'b', '2']
    result1 = db.search('record', search, 2)['data']
    result2 = db.search('record', search, 2, 3)
    assert len(result1) == 2 and len(result2['data']) == 1 and result2['count'] == 5

def test_tinydb_search_id(db):
    db.write('record', {'a': '1', 'b': '2'})
    uid = db.write('record', {'a': '1', 'b': '2'})['data']['added'][0]
    result = db.search('record', ['=', 'uid', uid])['data']
    assert len(result) == 1

def test_tinydb_delete(db):
    db.write('record', {'a': '1', 'b': '2'})
    db.write('record', {'a': '30', 'b': '40'})
    db.write('record', {'a': '100', 'b': '400'})
    search1 = ['OR', ['=', 'a', '1'], ['=', 'a', '30']]
    count = db.delete('record', search1)['count']
    result = db.search('record', search1)['data']
    assert count == 2 and len(result) == 0

def test_tinydb_delete_id(db):
    uid = db.write('record', {'a': '1', 'b': '2'})['data']['added'][0]
    count = db.delete('record', ['=', 'uid', uid])['count']
    assert count == 1

def test_tinydb_delete_all_fail(db):
    db.write('record', {'a': '1', 'b': '2'})
    db.write('record', {'a': '30', 'b': '40'})
    count = db.delete('record', [])['count']
    assert count == 0

def test_tinydb_delete_all_force(db):
    db.write('record', {'a': '1', 'b': '2'})
    db.write('record', {'a': '30', 'b': '40'})
    count = db.delete('record', {}, True)['count']
    assert count == 2

def test_tinydb_update_uid_with_primary(db):
    uid = db.write('record', {'a': '1', 'b': '2'}, 'a')['data']['added'][0]
    result = db.search('record', ['=', 'uid', uid])['data']
    result[0]['a'] = '2'
    updated = db.write('record', result, 'a')['data']['updated']
    result = db.search('record')['data']
    assert len(result) == 1 and len(updated) == 1 and result[0].items() >= {'a': '2', 'b': '2'}.items()

def test_tinydb_replace_uid_with_primary(db):
    uid = db.write('record', {'a': '1', 'b': '2'}, 'a')['data']['added'][0]
    result = db.search('record', ['=', 'uid', uid])['data']
    del result[0]['b']
    replaced = db.write('record', result, 'a', 'replace')['data']['replaced']
    assert len(replaced) == 1 and 'b' not in replaced[0]

def test_tinydb_update_uid_duplicate_primary(db):
    db.write('record', {'a': {'b': '1', 'c': '1'}}, 'a.b')
    uid = db.write('record', {'a': {'b': '2', 'c': '2'}}, 'a.b')['data']['added'][0]
    result = db.search('record', ['=', 'uid', uid])['data']
    result[0]['a']['b'] = '1'
    rejected = db.write('record', result, 'a.b')['data']['rejected']
    assert len(rejected) == 1

def test_tinydb_update_uid_constant(db):
    uid = db.write('record', {'a': '1', 'b': '2', 'c': 3})['data']['added'][0]
    result = db.search('record', ['=', 'uid', uid])['data']
    result[0]['c'] = '4'
    updated = db.write('record', result, constant=['a','b'])['data']['updated']
    result[0]['b'] = '1'
    rejected = db.write('record', result, constant=['a','b'])['data']['rejected']
    assert len(updated) == 1 and len(rejected) == 1

def test_tinydb_update_primary_constant(db):
    db.write('record', {'a': '1', 'b': '2', 'c': 3}, 'a')['data']['added'][0]
    updated = db.write('record',  {'a': '1', 'b': '2', 'c': 4}, 'a', constant='b')['data']['updated']
    rejected = db.write('record', {'a': '1', 'b': '1', 'c': 4}, 'a', constant='b')['data']['rejected']
    assert len(updated) == 1 and len(rejected) == 1

def test_tinydb_primary_duplicate_update(db):
    db.write('record', {'a': '1', 'b': '2'})
    updated = db.write('record', {'a': '1', 'b': '3'}, 'a')['data']['updated']
    result = db.search('record')['data']
    assert len(result) == 1 and len(updated) == 1 and result[0].items() >= {'a': '1', 'b': '3'}.items()

def test_tinydb_primary_duplicate_insert(db):
    db.write('record', {'a': '1', 'b': '2'})
    added = db.write('record', {'a': '1', 'b': '3'}, 'a', 'insert')['data']['added']
    result = db.search('record')['data']
    assert len(result) == 2 and len(added) == 1

def test_tinydb_primary_duplicate_reject(db):
    db.write('record', {'a': '1', 'b': '2'})
    rejected = db.write('record', {'a': '1', 'b': '3'}, 'a', 'reject')['data']['rejected']
    assert len(rejected) == 1

def test_tinydb_multiple_primary_update(db):
    db.write('record', {'a': '1', 'b': '1'})
    db.write('record', {'a': '1', 'b': '2'})
    db.write('record', {'a': '1', 'b': '3'})
    db.write('record', {'a': '1', 'b': '2', 'c': '3'}, 'a,b')
    result = db.search('record',  ['=', 'b', '2'])['data']
    assert len(result) == 1 and result[0].items() >= {'a': '1', 'b': '2', 'c': '3'}.items()

def test_tinydb_primary_duplicate_replace(db):
    db.write('record', {'a': '1', 'b': '2'})
    replaced = db.write('record', {'a': '1'}, 'a', 'replace')['data']['replaced']
    assert len(replaced) == 1 and 'b' not in replaced[0]

def test_tinydb_sort(db):
    db.write('record', [{'a': '1', 'b': '2'},{'a': '3', 'b': '2'},{'a': '2', 'b': '2'},{'a': '5', 'b': '2'},{'a': '4', 'b': '2'}])
    result = db.search('record', orderby='a', asc=False)['data']
    assert result[0].items() >= {'a': '5', 'b': '2'}.items()

def test_tinydb_sort_unknown(db):
    db.write('record', [{'a': '1', 'b': '2'},{'a': '3', 'b': '2'},{'a': '2', 'b': '2'},{'a': '5', 'b': '2'},{'a': '4', 'b': '2'}])
    result = db.search('record', orderby='c', asc=False)['data']
    assert result[0].items() >= {'a': '4', 'b': '2'}.items()

def test_tinydb_cleanup_timeout(db):
    db.write('record', [{'a': '1', 'ttl': 0}, {'b': '1', 'ttl': 0}, {'c': '1', 'ttl': 1}, {'d': '1'}])
    deleted_count = db.cleanup_timeout('record')
    assert deleted_count == 2

def test_tinydb_cleanup_orphans(db):
    uids = db.write('record', [{'a': '1'}, {'b': '1'}])['data']['added']
    db.write('comment', [{'record_uid': uids[0]}, {'record_uid': uids[1]}, {'record_uid': 'random'}])
    deleted_count = db.cleanup_orphans('comment', 'record_uid', 'record', 'uid')
    assert deleted_count == 1
