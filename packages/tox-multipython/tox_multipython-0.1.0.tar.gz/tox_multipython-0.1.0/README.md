# tox-multipython
> python interpreter interpreter discovery plugin for [tox](https://tox.wiki) 3 and [multipython](https://github.com/makukha/multipython)

[![license](https://img.shields.io/github/license/makukha/tox-multipython.svg)](https://github.com/makukha/tox-multipython/blob/main/LICENSE)
[![versions](https://img.shields.io/pypi/pyversions/tox-multipython.svg)](https://pypi.org/project/tox-multipython)
[![pypi](https://img.shields.io/pypi/v/tox-multipython.svg#v0.1.0)](https://pypi.python.org/pypi/tox-multipython)  
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

Read table below as

> When `tox-multipython` is installed inside `Host tag` environment, it allows to use selected ✅ *Target tag* as `env_list` in `tox.ini` and automatically discovers corresponding [multipython](https://hub.docker.com/r/makukha/multipython) executable. For rejected 🚫 *Target tag*, `tox` environment provision fails.

*Host tag* and *Target tags* are valid [multipython](https://hub.docker.com/r/makukha/multipython) tags.

<table>
<thead>
<tr>
    <th rowspan="2">Host tag</th>
    <th colspan="13">Target tag</th>
</tr>
<tr>
    <th><code>py</code><br/><code>314t</code></th>
    <th><code>py</code><br/><code>313t</code></th>
    <th><code>py</code><br/><code>314</code></th>
    <th><code>py</code><br/><code>313</code></th>
    <th><code>py</code><br/><code>312</code></th>
    <th><code>py</code><br/><code>311</code></th>
    <th><code>py</code><br/><code>310</code></th>
    <th><code>py</code><br/><code>39</code></th>
    <th><code>py</code><br/><code>38</code></th>
    <th><code>py</code><br/><code>37</code></th>
    <th><code>py</code><br/><code>36</code></th>
    <th><code>py</code><br/><code>35</code></th>
    <th><code>py</code><br/><code>27</code></th>
</tr>
</thead>
<tbody>
<!-- docsub: begin -->
<!-- docsub: exec bash .dev/gen-tests-summary.sh -->
<tr><th><code>py314t</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py313t</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py314</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py313</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py312</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py311</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py310</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py39</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py38</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py37</code></th> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>🚫</td> <td>🚫</td> <td>🚫</td></tr>
<tr><th><code>py36</code></th> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td></tr>
<tr><th><code>py35</code></th> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td></tr>
<tr><th><code>py27</code></th> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>🚫</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td> <td>✅</td></tr>
<!-- docsub: end -->
</tbody>
</table>

# Authors

* [Michael Makukha](https://github.com/makukha)

This package is a part of [multipython](https://github.com/makukha/multipython) project.


## License

[MIT License](https://github.com/makukha/caseutil/blob/main/LICENSE)


# Changelog

Check repository [CHANGELOG.md](https://github.com/makukha/tox-multipython/tree/main/CHANGELOG.md)
