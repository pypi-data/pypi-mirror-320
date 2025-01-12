FROM makukha/multipython:unsafe AS base
SHELL ["/bin/bash", "-o", "errexit", "-o", "errtrace", "-o", "nounset", "-o", "pipefail", "-c"]
COPY dist /test/dist
COPY tests/tox.ini /test/tests/
WORKDIR /test/tests
RUN <<EOT
    # remove version pre-installed with multipython
    python -m pip uninstall -y tox virtualenv-multipython
EOT


FROM base AS virtualenv_base
SHELL ["/bin/bash", "-o", "errexit", "-o", "errtrace", "-o", "nounset", "-o", "pipefail", "-c"]
ARG PYTHON_TAG
ARG VIRTUALENV_PIN
RUN <<EOT
    set -eEux -o pipefail
    PYTHON="$(py bin --path "${PYTHON_TAG}")"
    # install virtualenv and current plugin version
    $PYTHON -m pip install "virtualenv$VIRTUALENV_PIN" wheel
    $PYTHON -m pip install ../dist/*.whl
EOT


FROM virtualenv_base AS tox4
SHELL ["/bin/bash", "-o", "errexit", "-o", "errtrace", "-o", "nounset", "-o", "pipefail", "-c"]
ARG CASE_NAME
ARG VIRTUALENV_PIN
ARG TAGS_PASSING
ARG TAGS_NOTFOUND
RUN <<EOT
    set -eEux -o pipefail
    PYTHON="$(py bin --path "${PYTHON_TAG}")"
    echo_success () {
      echo "TEST CASE PASSED: ${CASE_NAME}" >&2
    }
    # verify tag coverage
    # shellcheck disable=SC2001
    INPUT_TAGS="$(sed 's/ /\n/g' <<<"$TAGS_PASSING $TAGS_NOTFOUND" | sort | xargs)"
    IMAGE_TAGS="$(py ls --tag | sort | xargs)"
    [ "$INPUT_TAGS" = "py20 $IMAGE_TAGS" ]

    # add tox
    $PYTHON -m pip install "tox>=4,<5" "virtualenv$VIRTUALENV_PIN" wheel
    TOX="$PYTHON -m tox -v"

    # run tests

    export VIRTUALENV_DISCOVERY=multipython
    export ENVS_PASSING="${TAGS_PASSING// /,}"
    export ENVS_NOTFOUND="${TAGS_NOTFOUND// /,}"
    export ENVS="${INPUT_TAGS// /,}"

    # passing
    $TOX run -m passing

    # not found
    for TAG in $TAGS_NOTFOUND; do
      [[ "$($TOX run -e $TAG)" == *" failed with could not find python "* ]]
    done

    echo_success
EOT


FROM virtualenv_base AS virtualenv
SHELL ["/bin/bash", "-o", "errexit", "-o", "errtrace", "-o", "nounset", "-o", "pipefail", "-c"]
ARG CASE_NAME
ARG PYTHON_TAG
ARG TAGS_PASSING
ARG TAGS_NOTFOUND
RUN <<EOT
    set -eEux -o pipefail
    PYTHON="$(py bin --path "${PYTHON_TAG}")"
    echo_success () {
      echo "TEST CASE PASSED: ${CASE_NAME}" >&2
    }
    # verify tag coverage
    # shellcheck disable=SC2001
    INPUT_TAGS="$(sed 's/ /\n/g' <<<"$TAGS_PASSING $TAGS_NOTFOUND" | sort | xargs)"
    IMAGE_TAGS="$(py ls --tag | sort | xargs)"
    [ "$INPUT_TAGS" = "py20 $IMAGE_TAGS" ]

    # run tests

    export VIRTUALENV_DISCOVERY=multipython

    # passing
    for TAG in $TAGS_PASSING
    do
      $PYTHON -m virtualenv -p "$TAG" --no-seed --with-traceback "/tmp/$TAG"
      [ "$(py tag "/tmp/$TAG/bin/python")" = "$TAG" ]
    done

    # failing
    for TAG in $TAGS_NOTFOUND
    do
      [[ "$($PYTHON -m virtualenv -p "$TAG" "/tmp/$TAG" 2>&1)" == *"RuntimeError: failed to find interpreter "* ]]
      [ ! -d "/tmp/$TAG" ]
    done

    echo_success
EOT
