# Originally based on Fedora spec file:
# https://src.fedoraproject.org/rpms/gns3-server/
#
# Modified to provide a single all-in-one gns3-server package  including
# dynamips, ubridge, vpcs, gns3-server and dependent python modules not
# available or overriden from the distro.
#
# When a new release of gns3-server is out, check the requirements.txt
# file and adjust python modules and versions accordingly.

%define dynamips_version 0.2.23
%define dynamips dynamips-%{dynamips_version}

%define ubridge_version 0.9.18
%define ubridge ubridge-%{ubridge_version}

%define vpcs_version 0.8.2
%define vpcs vpcs-%{vpcs_version}

%define python_aiohttp_cors aiohttp-cors-0.7.0
%define python_aiohttp aiohttp-3.8.3
%define python_aiosignal aiosignal-1.2.0
%define python_asynctest asynctest-0.13.0
%define python_async_timeout async-timeout-4.0.2
%define python_distro distro-1.7.0
%define python_frozenlist frozenlist-1.2.0
# idna-ssl available on el8 but not on el9
%define python_idna_ssl idna-ssl-1.1.0
%define python_importlib_resources importlib_resources-5.1.4
%define python_markupsafe MarkupSafe-2.0.0
%define python_psutil psutil-5.9.4
%define python_py_cpuinfo py-cpuinfo-9.0.0
# setuptools_scm is too old on el8
%define python_setuptools_scm setuptools_scm-6.0.1
# zipp is too old on el9
%define python_zipp zipp-3.1.0

%if 0%{?rhel} >= 9
%define python_aiofiles aiofiles-22.1.0
%define python_jinja2 Jinja2-3.1.2
%define python_jsonschema jsonschema-4.17.3
%define python_setuptools setuptools-65.5.1
%else
%define python_aiofiles aiofiles-0.8.0
%define python_jinja2 Jinja2-3.0.3
%define python_jsonschema jsonschema-3.2.0
%define python_setuptools setuptools-59.6.0
%endif

%define python_modules_build_order %(echo \\
    %{python_setuptools} \\
    %{python_setuptools_scm} \\
    %{python_aiofiles} \\
    %{python_async_timeout} \\
    %{python_frozenlist} \\
    %{python_aiosignal} \\
    %{python_asynctest} \\
    %{python_idna_ssl} \\
    %{python_aiohttp} \\
    %{python_aiohttp_cors} \\
    %{python_distro} \\
    %{python_markupsafe} \\
    %{python_zipp} \\
    %{python_importlib_resources} \\
    %{python_jinja2} \\
    %{python_jsonschema} \\
    %{python_psutil} \\
    %{python_py_cpuinfo} \\
)

%define py_base %{_datadir}/%{name}/py
%define py_site %{py_base}/lib/python%{python3_version}/site-packages
%define py_build_install \
(\
    export PYTHONUSERBASE=%{buildroot}/%{py_base}\
    python3 setup.py --no-user-cfg setopt -c easy_install -o index_url -s 'MISSING/'\
    python3 setup.py --no-user-cfg setopt -c easy_install -o find_links -s 'MISSING/'\
    python3 setup.py --no-user-cfg setopt -c easy_install -o zip_ok -s False\
    python3 setup.py --no-user-cfg build --debug\
    python3 setup.py --no-user-cfg install --skip-build --user --install-lib '%{buildroot}/%{py_site}'\
)\
%{nil}

# Filter auto-generated deps from shell script run in dockers,
# it would report bad requires:
# - /gns3/bin/busybox
# - /tmp/gns3/bin/sh
%global __requires_exclude_from ^%{py_site}/.*\.egg/gns3server/compute/docker/resources/.*$

Name: gns3-server22z
Version: 2.2.36
Release: 1%{?dist}.zenetys
Summary: Graphical Network Simulator 3

License: GPLv3
URL: http://gns3.com

Source0: https://github.com/GNS3/gns3-server/archive/v%{version}/%{name}-%{version}.tar.gz
Source1: gns3.service

Source110: https://github.com/GNS3/dynamips/archive/v%{dynamips_version}/%{dynamips}.tar.gz
Source120: https://github.com/GNS3/ubridge/archive/v%{ubridge_version}/%{ubridge}.tar.gz
Source130: https://github.com/GNS3/vpcs/archive/v%{vpcs_version}/%{vpcs}.tar.gz

Source210: https://files.pythonhosted.org/packages/source/a/aiofiles/%{python_aiofiles}.tar.gz
Source220: https://files.pythonhosted.org/packages/source/a/aiohttp/%{python_aiohttp}.tar.gz
Source230: https://files.pythonhosted.org/packages/source/a/aiohttp-cors/%{python_aiohttp_cors}.tar.gz
Source240: https://files.pythonhosted.org/packages/source/a/aiosignal/%{python_aiosignal}.tar.gz
Source250: https://files.pythonhosted.org/packages/source/a/asynctest/%{python_asynctest}.tar.gz
Source260: https://files.pythonhosted.org/packages/source/a/async-timeout/%{python_async_timeout}.tar.gz
Source270: https://files.pythonhosted.org/packages/source/d/distro/%{python_distro}.tar.gz
Source280: https://files.pythonhosted.org/packages/source/f/frozenlist/%{python_frozenlist}.tar.gz
Source285: https://files.pythonhosted.org/packages/source/i/idna-ssl/%{python_idna_ssl}.tar.gz
Source288: https://files.pythonhosted.org/packages/source/i/importlib-resources/%{python_importlib_resources}.tar.gz
Source290: https://files.pythonhosted.org/packages/source/J/Jinja2/%{python_jinja2}.tar.gz
Source300: https://files.pythonhosted.org/packages/source/j/jsonschema/%{python_jsonschema}.tar.gz
Source310: https://files.pythonhosted.org/packages/source/M/MarkupSafe/%{python_markupsafe}.tar.gz
Source320: https://files.pythonhosted.org/packages/source/p/psutil/%{python_psutil}.tar.gz
Source330: https://files.pythonhosted.org/packages/source/p/py-cpuinfo/%{python_py_cpuinfo}.tar.gz
Source340: https://files.pythonhosted.org/packages/source/s/setuptools/%{python_setuptools}.tar.gz
Source350: https://files.pythonhosted.org/packages/source/s/setuptools_scm/%{python_setuptools_scm}.tar.gz
Source360: https://files.pythonhosted.org/packages/source/z/zipp/%{python_zipp}.tar.gz

Patch300: jsonschema-4.17.3-build.patch

BuildRequires: busybox
BuildRequires: cmake
BuildRequires: elfutils-libelf-devel
BuildRequires: gcc
BuildRequires: elfutils-libelf-devel
BuildRequires: libcap
BuildRequires: libnl3-devel
BuildRequires: libpcap-devel
BuildRequires: make
BuildRequires: python3-attrs
BuildRequires: python3-charset-normalizer
BuildRequires: python3-devel
BuildRequires: python3-importlib-metadata
BuildRequires: python3-multidict
BuildRequires: python3-pyrsistent
BuildRequires: python3-setuptools

%if 0%{?rhel} >= 9
BuildRequires: python3-toml
%else
BuildRequires: python3-pytoml
BuildRequires: python3-wheel
%endif

BuildRequires: python3-six
BuildRequires: python3-sphinx
BuildRequires: python3-typing-extensions
BuildRequires: python3-yarl
BuildRequires: systemd

# needed for the privacy patch on index.html
BuildRequires: diffutils
BuildRequires: gawk

Requires: python3-attrs
Requires: python3-charset-normalizer
Requires: python3-importlib-metadata
Requires: python3-multidict
Requires: python3-pyrsistent
Requires: python3-six
Requires: python3-typing-extensions
Requires: python3-yarl
# script program is provided by util-linux
# it is required for docker support
Requires: util-linux

%{?systemd_requires}

Recommends: docker-ce
Recommends: qemu-kvm-core
Recommends: qemu-img

%description
GNS3 is a graphical network simulator that allows you to design complex network
topologies. You may run simulations or configure devices ranging from simple
workstations to powerful routers.

This is the server package which provides an HTTP REST API for the client (GUI).

%prep
%setup -n gns3-server-%{version}

# A patch file is difficult to maintain due to presence of a random id in patch
# context that would change on every release, obsolescing the patch file. This
# aims to remove the Google Analytics tracker and an ad panel.
cp -a gns3server/static/web-ui/index.html{,.ori}
gawk '
/<head>/ { print; print "<style type=\"text/css\">app-adbutler{display:none !important;}</style>"; next; }
/<script .*googletagmanager/ { print "<!--"; print; next; }
/gtag\(/ { print; getline; if (/<\/script>/) { print; print "-->"; next; } }
{ print; }
' < gns3server/static/web-ui/index.html.ori \
  > gns3server/static/web-ui/index.html
diff -u gns3server/static/web-ui/index.html{.ori,} && exit 4

# Relax requirements
sed -i -r 's/==/>=/g' requirements.txt
sed -i -r 's/sentry-sdk.*//g' requirements.txt

%setup -n gns3-server-%{version} -T -D -a 110
%setup -n gns3-server-%{version} -T -D -a 120
%setup -n gns3-server-%{version} -T -D -a 130

# python modules
for i in %python_modules_build_order; do
    tar xvzf "%{_sourcedir}/$i.tar.gz"
done

%if 0%{?rhel} >= 9
cd %{python_jsonschema}
%patch300 -p0
cd ..
%endif

%build
# Python modules missing or overriden from the distro are built and
# installed in the install scriptlet.

# dynamips
cd %{dynamips}
cmake \
    -DCMAKE_C_FLAGS="%{?build_cflags:%{build_cflags}} -g" \
    -DDYNAMIPS_CODE=stable \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_DOCDIR=%{_docdir}/%{name}/dynamips
cmake --build . -- %{?_smp_mflags}
cd ..

# ubridge
cd %{ubridge}
make %{?_smp_mflags} \
    CFLAGS='-DLINUX_RAW %{?build_cflags:%{build_cflags}} -g -lnl-3'
cd ..

# vpcs
cd %{vpcs}/src
sed -i -e 's,CFLAGS=.*,\0 $(LOCAL_CFLAGS),' Makefile.linux
make -f Makefile.linux %{?_smp_mflags} \
    LOCAL_CFLAGS='-DLINUX_RAW %{?build_cflags:%{build_cflags}} -g'
cd ../..

%install
# dynamips
cd %{dynamips}
DESTDIR=%{buildroot} cmake --install .
rm %{buildroot}/%{_docdir}/%{name}/dynamips/COPYING
install -p -m 0644 -D -t %{buildroot}/%{_datadir}/licenses/%{name}/dynamips COPYING
cd ..

# ubridge
cd %{ubridge}
install -p -m 4755 -D -t %{buildroot}/%{_bindir} ubridge
install -p -m 0644 -D -t %{buildroot}/%{_docdir}/%{name}/ubridge README.rst
install -p -m 0644 -D -t %{buildroot}/%{_datadir}/licenses/%{name}/ubridge LICENSE
cd ..

# vpcs
cd %{vpcs}
install -p -m 0755 -D -t %{buildroot}/%{_bindir} src/vpcs
install -p -m 0644 -D -t %{buildroot}/%{_docdir}/%{name}/vpcs readme.txt
install -p -m 0644 -D -t %{buildroot}/%{_datadir}/licenses/%{name}/vpcs COPYING
install -p -m 0644 -D -t %{buildroot}/%{_mandir}/man1 man/vpcs.1
cd ..

# python modules
for i in %python_modules_build_order; do
    cd "$i"
    %py_build_install
    cd ..
done

# gns3-server
%py_build_install

# Python wrapper with env PYTHONUSERBASE for bin scripts
echo $'#!/bin/sh\nPYTHONUSERBASE=%{py_base} exec /usr/bin/env python3 "$@"' \
    > %{buildroot}/%{py_base}/pywrap
chmod 755 %{buildroot}/%{py_base}/pywrap
sed -i -e '1i #!%{py_base}/pywrap' -e '1d' %{buildroot}/%{py_base}/bin/*
# Move gns3 scripts to system bin
mkdir -p %{buildroot}/%{_bindir}
mv %{buildroot}/%{py_base}/bin/{gns3loopback,gns3server,gns3vmnet} %{buildroot}/%{_bindir}/

# Remove python shebang in .py files
find %{buildroot}/%{py_base}/ -name '*.py' -print \
   -exec sed -i '1{\@^#!/usr/bin/env python@d}' {} \;

# Remove empty files
find %{buildroot}/ -type f -name .gitkeep -delete

# Build the docs
make -j8 -C docs html
rm docs/_build/html/.buildinfo

# Systemd service
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
mkdir -p  %{buildroot}%{_sharedstatedir}/gns3

# busybox binary from the distro is bundled in this package, make sure the
# build ID does not conflict with the one from the busybox package
%{_usr}/lib/rpm/debugedit --build-id --build-id-seed %{name}-%{version}-%{release} \
    %{buildroot}/%{py_site}/*.egg/gns3server/compute/docker/resources/bin/busybox

%files
# gns3-server
%license LICENSE
%doc README.rst AUTHORS CHANGELOG
%doc docs/_build/html
%{_bindir}/{gns3server,gns3vmnet,gns3loopback}
%{py_base}/
%{_unitdir}/gns3.service
%dir %attr(0755,gns3,gns3) %{_sharedstatedir}/gns3

# dynamips
%{_bindir}/{dynamips,nvram_export}
%{_docdir}/%{name}/dynamips/
%{_datadir}/licenses/%{name}/dynamips/
%{_mandir}/man*/{dynamips,nvram_export,hypervisor_mode}.*

# ubridge
%attr(0755,root,root) %caps(cap_net_admin,cap_net_raw=ep) %{_bindir}/ubridge
%{_docdir}/%{name}/ubridge/
%{_datadir}/licenses/%{name}/ubridge/

# vpcs
%{_bindir}/vpcs
%{_docdir}/%{name}/vpcs/
%{_datadir}/licenses/%{name}/vpcs/
%{_mandir}/man*/vpcs.*

%pre
if ! getent group gns3 >/dev/null; then
    groupadd -r gns3
fi
if ! getent passwd gns3 >/dev/null; then
    useradd -r -g gns3 -d %{_sharedstatedir}/gns3 -s /sbin/nologin \
        -c 'gns3 server' gns3
fi

%post
if [ -d %{_sharedstatedir}/gns3 ]; then
    chown -R gns3:gns3 %{_sharedstatedir}/gns3
fi
%systemd_post gns3.service

%preun
%systemd_preun gns3.service

%postun
%systemd_postun_with_restart gns3.service
