Supported targets:<br/>
el8, el9

This RPM spec file creates a single package:<br/>
gns3-server22z

Provides a single all-in-one gns3-server package  including dynamips, ubridge, vpcs, gns3-server and dependent python modules not available or overriden from the distro.

Build:

The package can be built easily using the rpmbuild-docker script provided in this repository. In order to use this script, _**a functional Docker environment is needed**_, with ability to pull Rocky Linux (el8, el9) images from internet if not already downloaded.

```
$ ./rpmbuild-docker -d el8
$ ./rpmbuild-docker -d el9
```

Prebuilt packages:

Builds of these packages are available on ZENETYS yum repositories:<br/>
https://packages.zenetys.com/latest/redhat/
