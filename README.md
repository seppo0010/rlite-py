# rlite-py

[![Build Status](https://travis-ci.org/seppo0010/rlite-py.svg?branch=master)](https://travis-ci.org/seppo0010/rlite-py)

Python bindings for rlite. For more information about rlite, go to
[rlite repository](https://github.com/seppo0010/rlite)

## Installation

```bash
$ pip install hirlite
```

## Usage

```python
>>> import hirlite
>>> rlite = hirlite.hirlite.Rlite()
>>> rlite.command('set', 'key', 'value')
True
>>> rlite.command('get', 'key')
'value'
```

### Unicode

```python
>>> rlite = hirlite.hirlite.Rlite(encoding='utf8')
>>> rlite.command('set', 'key', 'value')
True
>>> rlite.command('get', 'key')
u'value'
```

### Persistence

```python
>>> rlite = hirlite.hirlite.Rlite(path='mydb.rld')
>>> rlite.command('set', 'key', 'value')
True
>>> rlite = hirlite.hirlite.Rlite(path='mydb.rld')
>>> rlite.command('get', 'key')
'value'
```
