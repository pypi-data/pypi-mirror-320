# tox-multipython
> python interpreter interpreter discovery plugin for [tox](https://tox.wiki) 3 and [multipython](https://github.com/makukha/multipython)

[![license](https://img.shields.io/github/license/makukha/tox-multipython.svg)](https://github.com/makukha/tox-multipython/blob/main/LICENSE)
[![versions](https://img.shields.io/pypi/pyversions/tox-multipython.svg)](https://pypi.org/project/tox-multipython)
[![pypi](https://img.shields.io/pypi/v/tox-multipython.svg#v0.2.0)](https://pypi.python.org/pypi/tox-multipython)  
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/badge/uses-docsub-royalblue)
](https://github.com/makukha/docsub)

> [!NOTE]
> [tox-multipython]() has twin plugin [virtualenv-multipython](https://github.com/makukha/virtualenv-multipython) that serves the same purpose for [tox](https://tox.wiki) 4

This [tox](https://tox.wiki) plugin comes pre-installed in [multipython](https://hub.docker.com/r/makukha/multipython) Docker image and is responsible for resolving tox environment name to Python executable. Most probably, you don't need to install it yourself.

Environment names supported are all multipython tags, including free threading Python builds `py313t` and `py314t`. More names may be added in the future.

> [!IMPORTANT]
> This plugin does not fall back to tox python: interpreter discovery errors are explicit.

# Testing

There is one type of tests performed:
1. ***Tox 3.*** `tox` and `virtualenv` are installed in *host tag* environment, and `tox run` is executed on `tox.ini` with env names equal to *target tags*. Tox environment's python version must match tox env name and *target tag*. In these tests we test all [multipython](https://github.com/makukha/multipython) tags as both *host tags* and *target tags*.

Virtualenv supports discovery plugins since v20. In v20.22, it dropped support for Python <=3.6, in v20.27 it dropped support for Python 3.7.

This is why we use 3 different test setups:

1. ***Tox 3***, `tox>=3,<4`, `virtualenv>=20`
1. ***Tox 3***, `tox>=3,<4`, `virtualenv>=20,<20.27`
1. ***Tox 3***, `tox>=3,<4`, `virtualenv>=20,<20.22`

## Test report

When `tox-multipython` is installed inside *Host tag* environment, it allows to use selected ✅ *Target tag* as `env_list` in `tox.ini` and automatically discovers corresponding [multipython](https://hub.docker.com/r/makukha/multipython) executable. For rejected 🚫 *Target tag*, python executable is discovered, but `tox` environment provision fails.

*Host tag* and *Target tags* are valid [multipython](https://hub.docker.com/r/makukha/multipython) tags.

> [!NOTE]
> The fully green line for `py313` is a multipython design flaw that should be fixed soon: https://github.com/makukha/multipython/issues/76

<table>
<tbody>

<tr>
<td>
<code>tox>=3,<4</code>, <code>virtualenv>=20</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report tox3_venv -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
py314t  A ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
py313t  B ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
 py314  C ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
 py313  D ✅✅✅✅✅✅✅✅✅✅✅✅✅
 py312  E ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
 py311  F ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
 py310  G ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
  py39  H ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
  py38  I ✅✅✅✅✅✅✅✅✅🚫🚫🚫🚫
  py37  J ✅✅✅✅✅✅✅✅✅✅🚫🚫🚫
  py36  K 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
  py35  L 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
  py27  M 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
</pre>
<!-- docsub: end -->
</td>
</tr>

<tr>
<td>
<code>tox>=3,<4</code>, <code>virtualenv>=20,<20.27</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report tox3_venv27 -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
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
  py36  K 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
  py35  L 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
  py27  M 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
</pre>
<!-- docsub: end -->
</td>
</tr>

<tr>
<td>
<code>tox>=3,<4</code>, <code>virtualenv>=20,<20.22</code>
<!-- docsub: begin -->
<!-- docsub: exec uv run python docsubfile.py pretty-report tox3_venv22 -->
<!-- docsub: lines after 1 upto -1 -->
<pre>
          TARGETS
  HOST    A B C D E F G H I J K L M
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
  py36  K 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
  py35  L 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
  py27  M 🚫🚫🚫🚫🚫✅✅✅✅✅✅✅✅
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

Check repository [CHANGELOG.md](https://github.com/makukha/tox-multipython/tree/main/CHANGELOG.md)
