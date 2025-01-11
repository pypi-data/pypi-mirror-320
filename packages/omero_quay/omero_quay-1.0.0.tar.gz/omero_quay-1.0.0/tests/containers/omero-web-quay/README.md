OMERO.web Docker
================

[![Build Status](https://gitlab.in2p3.fr/fbi-data/dockers-projects/omero-web//badges/main/pipeline.svg)](https://gitlab.in2p3.fr/fbi-data/dockers-projects/omero-web)

A Ubuntu 20.04 based Docker image for OMERO.web.

Also see [SUPPORT.md](./SUPPORT.md)

Running OMERO with docker-compose
---------------------------------

Build the containers separately with docker build with these commands:

- In omero-web: docker build . --no-cache -t omeroweb:local

- In omero-web/standalone: docker build . --no-cache -t omeroweb-standalone:local

and make docker-compose up -d in minimal docker compose

Standalone image: omero-web-standalone
--------------------------------------

The quickest way to obtain a running OMERO.web server is to use
the [standalone image](https://hub.docker.com/r/openmicroscopy/omero-web-standalone/)
which uses the [WhiteNoise package](http://whitenoise.evans.io/en/stable/)
to avoid the need for Nginx.

This image also includes these OMERO.web plugins with a default configuration:
- [omero-figure](https://www.openmicroscopy.org/omero/figure/) (current version: 5.1.0)
- [omero-iviewer](https://www.openmicroscopy.org/omero/iviewer/) (current version: 0.12.0)
- [omero-fpbioimage](https://pypi.org/project/omero-fpbioimage/) (current version: 0.4.0)
- [omero-mapr](https://pypi.org/project/omero-mapr/) (current version: 0.5.0)
- [omero-parade](https://pypi.org/project/omero-parade/) (current version: 0.2.3)
- [parade-crossfilter](https://pypi.org/project/parade-crossfilter/) (current version: 0.0.5)
- [omero-webtagging-autotag](https://pypi.org/project/omero-webtagging-autotag/) (current version: 3.2.0)
- [omero-webtagging-tagsearch](https://pypi.org/project/omero-webtagging-tagsearch/) (current version: 3.2.0)
- [omero-forms](https://pypi.org/project/omero-webtagging-tagsearch/) (current version: 3.2.0)

To enable them or to change the configuration of a default plugin see the relevant plugin documentation.


To run the Docker image you can set a single OMERO.server to connect to by defining `OMEROHOST`:

    docker run -d --name omero-web \
        -e OMEROHOST=omero.example.org \
        -p 4080:4080 \
        openmicroscopy/omero-web-standalone

Alternatively, all configuration options can be set using environment variables, for example,
add the following arguments to the command above:

        -e CONFIG_omero_web_server__list='[["omero.example.org", 4064, "omero"]]' \
        -e CONFIG_omero_web_debug=true \

The `$OMERODIR` is `/opt/omero/web/OMERO.web/` so you can have the logs written to your host
by adding:

        -v /path/to/host/dir:/opt/omero/web/OMERO.web/var/logs \

Minimal OMERO.web image: omero-web
----------------------------------

[omero-web](https://hub.docker.com/r/openmicroscopy/omero-web/)
is a minimal OMERO.web image which requires additional configuration for serving Django static files.
For example, you can use https://github.com/dpwrussell/omero-nginx-docker


Configuration
-------------

All [OMERO configuration properties](https://docs.openmicroscopy.org/latest/omero/sysadmins/config.html) can be set be defining environment variables `CONFIG_omero_property_name=`.
Since `.` is not allowed in a variable name `.` must be replaced by `_`, and `_` by `__`.

Additional configuration files for OMERO can be provided by mounting files into `/opt/omero/web/config/`.
Files ending with `.omero` will be loaded with `omero load`.

See https://github.com/openmicroscopy/omero-server-docker for more details on configuration.


Default volumes
---------------

- `/opt/omero/web/OMERO.web/var`: The OMERO.web `var` directory, including logs


Exposed ports
-------------

- 4080
