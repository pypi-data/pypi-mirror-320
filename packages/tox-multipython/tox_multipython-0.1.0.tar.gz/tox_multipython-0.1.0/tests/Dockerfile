FROM makukha/multipython:unsafe

RUN <<EOT
    # remove version pre-installed with multipython
    python -m pip uninstall -y tox virtualenv-multipython
EOT

COPY dist /test/dist
COPY tests/tox.*.ini /test/tests/
WORKDIR /test

ARG TOX_TAG
RUN <<EOT
    set -eEux -o pipefail
    # install tox and current plugin version
    $(py bin --path "$TOX_TAG") -m pip install tox wheel
    $(py bin --path "$TOX_TAG") -m pip install dist/*.whl
EOT

ARG TAGS_PASSING
ARG TAGS_INVALID
ARG TAGS_NOTFOUND
RUN <<EOT
    set -eEux -o pipefail
    TOX="$(py bin --path "$TOX_TAG") -m tox"
    # make sure all tags mentioned
    (sed 's/ /\n/g' <<<"$TAGS_PASSING $TAGS_INVALID" | sort) | diff -s - <(py ls --tag | sort)

    cd tests
    # this is needed to not interfere with virtualenv-multipython
    export VIRTUALENV_DISCOVERY=

    # passing
    sed 's/{env:ENVS}/'"$(tr ' ' , <<<"$TAGS_PASSING")"'/' tox.passing.ini > tox.ini
    $TOX run -e ALL -v
    # invalid
    sed 's/{env:ENVS}/'"$(tr ' ' , <<<"$TAGS_INVALID")"'/' tox.failing.ini > tox.ini
    for TAG in $TAGS_INVALID; do
      [[ "$($TOX run -e $TAG)" == *" invocation failed "* ]]
    done
    # not found
    sed 's/{env:ENVS}/'"$(tr ' ' , <<<"$TAGS_NOTFOUND")"'/' tox.failing.ini > tox.ini
    for TAG in $TAGS_NOTFOUND; do
      [[ "$($TOX run -e $TAG)" == *" InterpreterNotFound:"* ]]
    done
EOT
