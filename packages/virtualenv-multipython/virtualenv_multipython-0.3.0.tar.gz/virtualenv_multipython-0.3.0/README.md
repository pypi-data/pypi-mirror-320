# virtualenv-multipython
> virtualenv discovery plugin for [multipython](https://github.com/makukha/multipython)

[![license](https://img.shields.io/github/license/makukha/virtualenv-multipython.svg)](https://github.com/makukha/virtualenv-multipython/blob/main/LICENSE)
[![versions](https://img.shields.io/pypi/pyversions/virtualenv-multipython.svg)](https://pypi.org/project/virtualenv-multipython)
[![pypi](https://img.shields.io/pypi/v/virtualenv-multipython.svg#v0.3.0)](https://pypi.python.org/pypi/virtualenv-multipython)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)

> [!NOTE]
> [virtualenv-multipython]() has twin plugin [tox-multipython](https://github.com/makukha/tox-multipython) that serves the same purpose for [tox](https://tox.wiki) 3

This [virtualenv](https://virtualenv.pypa.io) plugin comes pre-installed in [multipython](https://hub.docker.com/r/makukha/multipython) Docker image and is responsible for resolving tox environment name to Python executable. Most probably, you don't need to install it yourself.

Environment names supported are all multipython tags, including free threading Python builds `py313t` and `py314t`. More names may be added in the future.

> [!IMPORTANT]
> This plugin does not fall back to tox python: interpreter discovery errors are explicit.

# Testing

There are two types of tests performed, both with env var `VIRTUALENV_DISCOVERY=multipython` exported:
1. ***Virtualenv.*** Install `virtualenv` in *host tag* environment and create virtual environments for all *target tags*. Environment's python version must match *target tag*. In these tests we test all [multipython](https://github.com/makukha/multipython) tags as both *host tags* and *target tags*.
2. ***Tox 4.*** Install `tox` and `virtualenv` are installed in *host tag* environment, and `tox run` is executed on `tox.ini` with env names equal to *target tags*. Tox environment's python version must match tox env name and *target tag*. In these tests we test all [multipython](https://github.com/makukha/multipython) tags as *target tags* and all tags except `py27`, `py35`, `py36` as *target tags* (because tox 4 is requires Python 3.7+).

Virtualenv supports discovery plugins since v20. In v20.22, it dropped support for Python <=3.6, in v20.27 it dropped support for Python 3.7. You will see below that it is still capable to *discover* 3.7, but probably those 3.7 environments won't be fully functional.

This is why we use 6 different test setups:

1. ***Virtualenv***, `virtualenv>=20`
1. ***Virtualenv***, `virtualenv>=20,<20.27`
1. ***Virtualenv***, `virtualenv>=20,<20.22`
1. ***Tox 4***, `tox>=4,<5`, `virtualenv>=20`
1. ***Tox 4***, `tox>=4,<5`, `virtualenv>=20,<20.27`
1. ***Tox 4***, `tox>=4,<5`, `virtualenv>=20,<20.22`

## Test reports

When `virtualenv-multipython` is installed inside *Host tag* environment, it allows to use selected ✅ *Target tag* (create virtualenv environment or use as tox env name in `env_list`) and automatically discovers corresponding [multipython](https://github.com/makukha/multipython) executable. For failing 🚫️ *Target tag*, python executable is not discoverable.

*Host tag* and *Target tags* are valid [multipython](https://hub.docker.com/r/makukha/multipython) tags. *Host tags* are listed vertically (rows), *target tags* are listed horizontally (columns).


### 

<table>
<tbody>

<tr>

<td>
<code>virtualenv>=20</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report venv -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
py314t  A ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
py313t  B ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py314  C ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py313  D ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py312  E ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py311  F ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py310  G ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py39  H ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py38  I ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py37  J ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py36  K ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py35  L ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py27  M ✅✅✅✅✅✅✅✅✅✅✅✅✅
</pre>
<!-- docsub: end -->
</td>

<td>
<code>tox>=4,<5</code>, <code>virtualenv>=20</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report tox4_venv -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
py314t  A ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
py313t  B ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py314  C ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py313  D ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py312  E ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py311  F ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py310  G ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py39  H ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py38  I ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py37  J ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py36  K 
  py35  L 
  py27  M 
</pre>
<!-- docsub: end -->
</td>

</tr>

<tr>

<td>
<code>virtualenv>=20,<20.27</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report venv27 -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
py314t  A ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
py313t  B ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py314  C ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py313  D ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py312  E ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py311  F ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py310  G ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py39  H ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py38  I ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py37  J ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py36  K ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py35  L ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py27  M ✅✅✅✅✅✅✅✅✅✅✅✅✅
</pre>
<!-- docsub: end -->
</td>

<td>
<code>tox>=4,<5</code>, <code>virtualenv>=20,<20.27</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report tox4_venv27 -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
py314t  A ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
py313t  B ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py314  C ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py313  D ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py312  E ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py311  F ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
 py310  G ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py39  H ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py38  I ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py37  J ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py36  K 
  py35  L 
  py27  M 
</pre>
<!-- docsub: end -->
</td>

</tr>

<tr>

<td>
<code>virtualenv>=20,<20.22</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report venv22 -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
py314t  A ✅✅✅✅✅✅✅✅✅✅✅✅✅
py313t  B ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py314  C ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py313  D ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py312  E ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py311  F ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py310  G ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py39  H ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py38  I ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py37  J ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py36  K ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py35  L ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py27  M ✅✅✅✅✅✅✅✅✅✅✅✅✅
</pre>
<!-- docsub: end -->
</td>

<td>
<code>tox>=4,<5</code>, <code>virtualenv>=20,<20.22</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report tox4_venv22 -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
py314t  A ✅✅✅✅✅✅✅✅✅✅✅✅✅
py313t  B ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py314  C ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py313  D ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py312  E ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py311  F ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py310  G ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py39  H ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py38  I ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py37  J ✅✅✅✅✅✅✅✅✅✅✅✅✅
  py36  K 
  py35  L 
  py27  M 
</pre>
<!-- docsub: end -->
</td>

</tr>

</tbody>
</table>


# Authors

* [Michael Makukha](https://github.com/makukha)

This package is a part of [multipython](https://github.com/makukha/multipython) project.


## License

[MIT License](https://github.com/makukha/caseutil/blob/main/LICENSE)


# Changelog

Check repository [CHANGELOG.md](https://github.com/makukha/virtualenv-multipython/tree/main/CHANGELOG.md)
