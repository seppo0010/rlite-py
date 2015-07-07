# rlite-py

[![Build Status](https://travis-ci.org/seppo0010/rlite-py.svg?branch=master)](https://travis-ci.org/seppo0010/rlite-py) [![PyPI version](https://badge.fury.io/py/hirlite.svg)](http://badge.fury.io/py/hirlite)

Python bindings for rlite. For more information about rlite, go to
[rlite repository](https://github.com/seppo0010/rlite)

## Installation

```bash
$ pip install hirlite
```

## Usage

```python
>>> import hirlite
>>> rlite = hirlite.Rlite()
>>> rlite.command('set', 'key', 'value')
True
>>> rlite.command('get', 'key')
'value'
```

### Unicode

```python
>>> rlite = hirlite.Rlite(encoding='utf8')
>>> rlite.command('set', 'key', 'value')
True
>>> rlite.command('get', 'key')
u'value'
```

### Persistence

```python
>>> rlite = hirlite.Rlite(path='mydb.rld')
>>> rlite.command('set', 'key', 'value')
True
>>> rlite = hirlite.Rlite(path='mydb.rld')
>>> rlite.command('get', 'key')
'value'
```

### Pubsub

```python
>>> subscriber = hirlite.Rlite(path='mydb.rld')
>>> subscriber.command('subscribe', 'channel', 'channel2')
['subscribe', 'channel', 1L]
>>> subscriber.command('__rlite_poll')
['subscribe', 'channel2', 2L]
>>> subscriber.command('__rlite_poll')
>>> publisher = hirlite.Rlite(path='mydb.rld')
>>> publisher.command('publish', 'channel', 'hello world')
1L
>>> subscriber.command('__rlite_poll')
['message', 'channel', 'hello world']
>>> subscriber.command('__rlite_poll')
>>>
```
