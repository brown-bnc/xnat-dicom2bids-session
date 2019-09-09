#!/bin/bash

# Builds and pushes a given image to gcr.io + all nodes in current kubectl
# context
set -e

DOCKER_REPO="brownbnc"
DOCKER_PUSH="docker push"
FORCE=False
SKIP_PUSH=False
export NAMED_TAG="latest"

usage() {
	echo "Usage:"
	echo "     -h – help"
	echo "     -t – Tag e.g., fall-19"
	echo " 	   -s - Skip push"
	echo "     -f – Force build";
}

while getopts h:t:fs opt; do
    echo $opt
	case "${opt}" in
		f) FORCE=True;;
		s) SKIP_PUSH=True;;
		t) NAMED_TAG=${OPTARG};;
		h) usage; exit;;
	esac
done
shift $((OPTIND-1))


# Bail if we're on a dirty git tree
echo "Force Build? $FORCE"
if ! $FORCE; then
	if ! git diff-index --quiet HEAD; then
		echo "You have uncommited changes. Please commit them before building and"
		echo "populating. This helps ensure that all docker images are traceable"
		echo "back to a git commit."
		exit 1
	fi
fi

GIT_REV=$(git log -n 1 --pretty=format:%h -- ${IMAGE})
TAG="${GIT_REV}"

IMAGE="$1"

echo "Building $IMAGE"
if [ ! -f ${IMAGE}/Dockerfile ]; then
echo "No such file: ${IMAGE}/Dockerfile"
exit 1
fi

IMAGE_SPEC="${DOCKER_REPO}/${IMAGE}:${TAG}"
docker build -f Dockerfile -t ${IMAGE_SPEC} .
docker tag ${DOCKER_REPO}/${IMAGE}:${TAG} ${DOCKER_REPO}/${IMAGE}:${NAMED_TAG}

echo "Build ${IMAGE_SPEC} and ${DOCKER_REPO}/${IMAGE}:${NAMED_TAG}"

echo "Skip Push? $SKIP_PUSH"

if ! $SKIP_PUSH; then
    echo "Pushed images"
    ${DOCKER_PUSH} ${IMAGE_SPEC}
    ${DOCKER_PUSH} ${DOCKER_REPO}/${IMAGE}:${NAMED_TAG}
fi



