#!/bin/bash
docker run -v ~/github/OAuth2OOo:/src -v ./_fascan.yml:/fascan.yml fluidattacks/cli:latest skims scan /fascan.yml
#docker system prune -f
