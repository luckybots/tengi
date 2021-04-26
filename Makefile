# We use "pwd" as this Makefile is usually imported from outside and we want to reference outer Makefile working
#   directory
CURRENT_PATH := $(shell pwd)
CURRENT_DIR := $(shell basename ${CURRENT_PATH})

DOCKER_IMAGE := ${CURRENT_DIR}
DOCKER_CONTAINER := ${CURRENT_DIR}

ADDITIONAL_OPTIONS := ""
DOCKER_RUN_CMD = \
	if [ $$(docker ps -q -f name=${DOCKER_CONTAINER}) ]; then \
                docker kill --signal SIGINT ${DOCKER_CONTAINER}; \
	fi; \
        if [ $$(docker ps --all -q -f name=${DOCKER_CONTAINER}) ]; then \
                docker rm -f ${DOCKER_CONTAINER}; \
        fi; \
	docker run \
		--init \
		--name ${DOCKER_CONTAINER} \
		-v ${PWD}/data:/app/data \
		--user $$(id -u):$$(id -g) \
		$${ADDITIONAL_OPTIONS} \
		${DOCKER_IMAGE}



.PHONY: list
vars:
	echo Docker image: ${DOCKER_IMAGE}

build:
	@echo "Building ${DOCKER_CONTAINER} docker image"; \
	docker build . -t ${DOCKER_IMAGE}

run-it:
	@echo "Running ${DOCKER_CONTAINER} interactively"; \
	export ADDITIONAL_OPTIONS="-it --rm"; \
	${DOCKER_RUN_CMD}

run-daemon:
	@echo "Running ${DOCKER_CONTAINER} as daemon"; \
	export ADDITIONAL_OPTIONS="-d --restart=always"; \
        ${DOCKER_RUN_CMD}

stop:
	@if [ $$(docker ps -aq -f name=${DOCKER_CONTAINER}) ]; then \
		if [ $$(docker ps -q -f name=${DOCKER_CONTAINER}) ]; then \
		    echo 'Stopping container ...'; \
			docker stop ${DOCKER_CONTAINER} || /bin/true; \
		fi; \
		echo 'Removing container...'; \
		docker rm -f ${DOCKER_CONTAINER}; \
	else \
	    echo "Container ${DOCKER_CONTAINER} does not exist"; \
	fi

