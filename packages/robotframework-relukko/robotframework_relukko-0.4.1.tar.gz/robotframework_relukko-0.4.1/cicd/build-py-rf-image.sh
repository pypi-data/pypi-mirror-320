#!/bin/sh

set -e

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
REPO_DIR="${SCRIPT_DIR}/.."
CONTAINER_DIR="${REPO_DIR}/container"
CONTAINER_CMD="docker"

# IMAGE_NAME should normally come from .gitlab-ci.yml file,
# set default for local usage.
if [ -z "${IMAGE_NAME+x}" ]; then
    IMAGE_NAME=py-rf-image-local
fi

cd "${CONTAINER_DIR}" || exit

${CONTAINER_CMD} build -t "${IMAGE_NAME}:latest" --file Containerfile .

${CONTAINER_CMD} images

if [ -n "${CI_REGISTRY_IMAGE}" ]; then
    # In Gitlab

    # Tag with Git commit short sha and push
    IMAGE_WITH_GIT_SHA="${CI_REGISTRY_IMAGE}/${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA}"
    echo "IMAGE_WITH_GIT_SHA: ${IMAGE_WITH_GIT_SHA}"

    ${CONTAINER_CMD} tag "${IMAGE_NAME}:latest" "${IMAGE_WITH_GIT_SHA}"
    ${CONTAINER_CMD} push "${IMAGE_WITH_GIT_SHA}"

    if [ "${CI_COMMIT_BRANCH}" = "${CI_DEFAULT_BRANCH}" ]; then
        # We run in default branch, also tag with latest
        # Tag with "latest" (overwrites last 'latest' in registry) and push
        IMAGE_WITH_LATEST="${CI_REGISTRY_IMAGE}/${IMAGE_NAME}:latest"

        echo "Tag image with as 'latest': ${IMAGE_WITH_LATEST}"

        ${CONTAINER_CMD} tag "${IMAGE_NAME}:latest" "${IMAGE_WITH_LATEST}"
        ${CONTAINER_CMD} push "${IMAGE_WITH_LATEST}"
    fi
else
    echo "Runs locally, no pushing!"
fi

cd -

# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab: