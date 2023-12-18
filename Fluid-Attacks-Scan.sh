#!/bin/bash

docker run -v ~/github/OAuth2OOo:/working-dir ghcr.io/fluidattacks/makes/amd64 m gitlab:fluidattacks/universe@trunk /skims scan ./_fascan.yml
