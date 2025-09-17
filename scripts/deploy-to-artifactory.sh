#!/bin/bash -ex

PUSH_TO_ARTIFACTORY=true # set this to false if need to be tested locally
ONLY_TAG=false
IMAGE_NAME="stardog-cloud-mcp"

if [[ -z "${1-}" ]]; then        # no argument supplied - create manifest only
  ONLY_TAG=true
  ARCH=""
else                             # at least one argument present - build for specific arch
  ONLY_TAG=false
  ARCH="$1"
fi

if [ "$ONLY_TAG" = false ]; then
  echo "Building Docker image for architecture: ${ARCH}"
  # Build the Docker image using make command
  make docker-build
fi

if [ "$PUSH_TO_ARTIFACTORY" = true ]; then
  export ARTIFACTORY_REGISTRY_INTERNAL=stardog-testing-docker.jfrog.io
  export ARTIFACTORY_REGISTRY_EXTERNAL=stardog-stardog-apps.jfrog.io

  # Create the docker tag by the git tag if there is one otherwise
  # we default to the branch name (develop/main)
  export BRANCH=${CIRCLE_BRANCH:-unstable}
  export GIT_TAG=${CIRCLE_TAG:-$BRANCH}
  export TAG=${TAG:-$GIT_TAG}

  # Check to see if we are pushing the main branch if so change the Docker tag
  # and push images to the internal registry. When CIRCLE_TAG is set that indicates
  # we are doing a release and the image is pushed to the external registry
  if [ "${TAG}" = "main" ]; then
    echo "Building images for main"
    # Switch the tag to include timestamp
    TAG=${TAG}-${CIRCLE_SHA1:0:7}-$(date +%Y%m%d%H%M)
  fi

  if [ -z "${ARTIFACTORY_PASSWORD}" ]; then
    echo "Missing artifactory password!"
    exit 1
  fi

  if [ -z "${ARTIFACTORY_USERNAME}" ]; then
    echo "Missing artifactory username"
    exit 1
  fi

  echo "Logging into internal docker registry"
  docker login ${ARTIFACTORY_REGISTRY_INTERNAL} -u ${ARTIFACTORY_USERNAME} -p ${ARTIFACTORY_PASSWORD}

  if [ "$ONLY_TAG" = true ]; then
    echo "Creating and pushing the ${IMAGE_NAME} manifest with tag: ${TAG}"
    docker buildx imagetools create \
      -t ${ARTIFACTORY_REGISTRY_INTERNAL}/cloud/${IMAGE_NAME}:${TAG} \
      ${ARTIFACTORY_REGISTRY_INTERNAL}/cloud/${IMAGE_NAME}:${TAG}-amd64 \
      ${ARTIFACTORY_REGISTRY_INTERNAL}/cloud/${IMAGE_NAME}:${TAG}-arm64

  else
    echo "Tagging and pushing the ${IMAGE_NAME} image with tag: ${TAG}-${ARCH}"
    docker tag ${IMAGE_NAME} ${ARTIFACTORY_REGISTRY_INTERNAL}/cloud/${IMAGE_NAME}:${TAG}-${ARCH}
    docker push ${ARTIFACTORY_REGISTRY_INTERNAL}/cloud/${IMAGE_NAME}:${TAG}-${ARCH}
  fi

  # If this is a version tag (v1.0.0 format), push to external registry as well
  if [[ "${TAG}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Detected version tag: ${TAG}"
    echo "Logging into external docker registry"
    docker login ${ARTIFACTORY_REGISTRY_EXTERNAL} -u ${ARTIFACTORY_USERNAME} -p ${ARTIFACTORY_PASSWORD}

    if [ "$ONLY_TAG" = true ]; then
      echo "Creating and pushing the ${IMAGE_NAME} manifest with tag: ${TAG}"
      docker buildx imagetools create \
        -t ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:${TAG} \
        ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:${TAG}-amd64 \
        ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:${TAG}-arm64

      echo "Creating and pushing the ${IMAGE_NAME} manifest with tag: current"
      docker buildx imagetools create \
        -t ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:current \
        ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:current-amd64 \
        ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:current-arm64

      echo "Creating and pushing the ${IMAGE_NAME} manifest with tag: latest"
      docker buildx imagetools create \
        -t ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:latest \
        ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:latest-amd64 \
        ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:latest-arm64
    else
      echo "Tagging and pushing the ${IMAGE_NAME} image with tag: ${TAG}-${ARCH}"
      docker tag ${IMAGE_NAME} ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:${TAG}-${ARCH}
      docker push ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:${TAG}-${ARCH}
      
      echo "Tagging and pushing ${IMAGE_NAME} image to ${ARTIFACTORY_REGISTRY_EXTERNAL} with tag: current-${ARCH}"
      docker tag ${IMAGE_NAME} ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:current-${ARCH}
      docker push ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:current-${ARCH}

      echo "Tagging and pushing ${IMAGE_NAME} image to ${ARTIFACTORY_REGISTRY_EXTERNAL} with tag: latest-${ARCH}"
      docker tag ${IMAGE_NAME} ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:latest-${ARCH}
      docker push ${ARTIFACTORY_REGISTRY_EXTERNAL}/${IMAGE_NAME}:latest-${ARCH}
    fi
  fi
else
    echo "Skipping push to artifactory"
fi