FROM makukha/multipython:unsafe
SHELL ["/bin/bash", "-o", "errexit", "-o", "errtrace", "-o", "nounset", "-o", "pipefail", "-c"]
RUN <<EOT
    # remove version pre-installed with multipython
    python -m pip uninstall -y tox virtualenv-multipython
EOT

COPY dist /test/dist
WORKDIR /test/tests

ARG PYTHON_TAG
ARG VIRTUALENV_PIN
RUN <<EOT
    set -eEux -o pipefail
    PYTHON="$(py bin --path "${PYTHON_TAG}")"
    # install tox and current plugin version
    $PYTHON -m pip install "tox>=3,<4" wheel
    $PYTHON -m pip install ../dist/*.whl
EOT

COPY tests/tox.*.ini /test/tests/
ARG CASE_NAME
ARG TAGS_PASSING
ARG TAGS_FAILING
ARG TAGS_NOTFOUND
RUN <<EOT
    set -eEux -o pipefail
    PYTHON="$(py bin --path "${PYTHON_TAG}")"
    echo_success () {
      echo "TEST CASE PASSED: ${CASE_NAME}" >&2
    }
    # verify tag coverage
    # shellcheck disable=SC2001
    INPUT_TAGS="$(sed 's/  */\n/g' <<<"$TAGS_PASSING $TAGS_FAILING $TAGS_NOTFOUND" | sort | xargs)"
    IMAGE_TAGS="$(py ls --tag | sort | xargs)"
    [ "$INPUT_TAGS" = "py20 $IMAGE_TAGS" ]

    # add tox
    $PYTHON -m pip install "tox>=3,<4" "virtualenv$VIRTUALENV_PIN" wheel
    TOX="$PYTHON -m tox -v"

    # run tests

    # this is needed to not interfere with virtualenv-multipython
    export VIRTUALENV_DISCOVERY=

    # passing
    sed 's/{env:ENVS}/'"${TAGS_PASSING// /,}"'/' tox.passing.ini > tox.ini
    $TOX run

    # invalid
    if [ -n "$TAGS_FAILING" ]; then
        sed 's/{env:ENVS}/'"${TAGS_FAILING// /,}"'/' tox.failing.ini > tox.ini
        for TAG in $TAGS_FAILING; do
          [[ "$($TOX run -e $TAG)" == *" invocation failed "* ]]
        done
    fi

    # not found
    sed 's/{env:ENVS}/'"${TAGS_NOTFOUND// /,}"'/' tox.failing.ini > tox.ini
    for TAG in $TAGS_NOTFOUND; do
      [[ "$($TOX run -e $TAG)" == *" InterpreterNotFound:"* ]]
    done

    echo_success
EOT
