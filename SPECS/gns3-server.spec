# Supported targets: el8, el9

%define gns3server_version 3.0.5
%define gns3server gns3-server-%{gns3server_version}

%define dynamips_version 0.2.23
%define dynamips dynamips-%{dynamips_version}

%define ubridge_version 0.9.19
%define ubridge ubridge-%{ubridge_version}

%define vpcs_version 0.8.3
%define vpcs vpcs-%{vpcs_version}

%define py_version 3.9
%define py_base %{_datadir}/%{name}/py
%define py_build_extra 'setuptools>=61.0' 'wheel'
%define py_mod_bundle_sig_meta %{py_version}_%{_arch}_%{?dist}

# Filter auto-generated deps from shell script run in dockers,
# it would report bad requires:
# - /gns3/bin/busybox
# - /tmp/gns3/bin/sh
%global __requires_exclude_from ^%{py_base}/.*/gns3server/compute/docker/resources/.*$

Name: gns3-server-30z
Version: %{gns3server_version}
Release: 1%{?dist}.zenetys
Summary: Graphical Network Simulator 3

License: GPLv3
URL: http://gns3.com

Source0: https://github.com/GNS3/gns3-server/archive/v%{version}/%{gns3server}.tar.gz
Source1: gns3.service
Patch0: gns3-server-3.0.0-disable-tracking.patch

Source110: https://github.com/GNS3/dynamips/archive/v%{dynamips_version}/%{dynamips}.tar.gz
Source120: https://github.com/GNS3/ubridge/archive/v%{ubridge_version}/%{ubridge}.tar.gz
Source130: https://github.com/GNS3/vpcs/archive/v%{vpcs_version}/%{vpcs}.tar.gz

BuildRequires: cmake
BuildRequires: elfutils-libelf-devel
BuildRequires: gawk
BuildRequires: gcc
BuildRequires: libcap
BuildRequires: libnl3-devel
BuildRequires: libpcap-devel
BuildRequires: make
BuildRequires: python%{py_version}
BuildRequires: python%{py_version}dist(pip)
BuildRequires: sed
BuildRequires: systemd

Requires: python%{py_version}
# script program is provided by util-linux
# it is required for docker support
Requires: util-linux

%{?systemd_requires}

# busybox is available in epel repos
# - el8: epel-next
# - el9: epel
Recommends: busybox
Recommends: docker-ce
Recommends: qemu-kvm-core
Recommends: qemu-img

%description
GNS3 is a graphical network simulator that allows you to design complex network
topologies. You may run simulations or configure devices ranging from simple
workstations to powerful routers.

This is the server package which provides an HTTP REST API for the client (GUI).

%prep
%setup -c -T

# gns3-server
%setup -T -D -a 0
cd %{gns3server}
# gns3-server 3.0.5
# ERROR: Double requirement given: async-timeout<5.1,>=5.0.1 (from
# -r requirements.txt (line 12)) (already in async-timeout==5.0.1
# (from -r requirements.txt (line 7)), name='async-timeout')
sed -i -e '/^async-timeout>=5\.0\.1,<5\.1$/d' requirements.txt

# Patch web-ui index.html to remove the Google Analytics tracker and an ad panel.
# The patch is difficult to maintain due to presence of a random id in patch
# context that changes on every release, hence this little trick...
gns3ui_js=$(grep -E '<script src="(runtime|polyfills|main)\.' gns3server/static/web-ui/index.html |sed -zre 's,\n(.),\x16\1,g')
gawk -v "gns3ui_js=$gns3ui_js" '/<!-- gns3ui js script/ { print " " gns3ui_js; next; } { print; }' %{PATCH0} |
    patch -p1 -b -z .gtag
sed -i -re 's,\x16,\n,g' gns3server/static/web-ui/index.html
diff -u gns3server/static/web-ui/index.html{.gtag,} && exit 4
# python modules
sig=$({ cat requirements.txt; echo %{py_build_extra} %{py_mod_bundle_sig_meta}; } |
    md5sum |gawk '{print $1}')
if [ -f "%_sourcedir/pymod_${sig}.tar.xz" ]; then
    tar xvJf "%{_sourcedir}/pymod_${sig}.tar.xz" -C ../
else
    pip%{py_version} download \
        --no-cache-dir \
        --dest "../pymod_${sig}" \
        --progress-bar off \
        -r requirements.txt %{py_build_extra}
    tar cJf "%{_sourcedir}/pymod_${sig}.tar.xz" \
        "../pymod_${sig}"
fi
cd ..

# dynamips
%setup -T -D -a 110

# ubridge
%setup -T -D -a 120

# vpcs
%setup -T -D -a 130

%build
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
install -p -m 0644 -D -t %{buildroot}/%{_docdir}/%{name}/ubridge README.md
install -p -m 0644 -D -t %{buildroot}/%{_datadir}/licenses/%{name}/ubridge LICENSE
cd ..

# vpcs
cd %{vpcs}
install -p -m 0755 -D -t %{buildroot}/%{_bindir} src/vpcs
install -p -m 0644 -D -t %{buildroot}/%{_docdir}/%{name}/vpcs readme.txt
install -p -m 0644 -D -t %{buildroot}/%{_datadir}/licenses/%{name}/vpcs COPYING
install -p -m 0644 -D -t %{buildroot}/%{_mandir}/man1 man/vpcs.1
cd ..

# gns3-server
cd %{gns3server}
mkdir -p %{buildroot}/%{py_base}/lib
ln -s lib %{buildroot}/%{py_base}/%{_lib} # lib64 -> lib
sig=$({ cat requirements.txt; echo %{py_build_extra} %{py_mod_bundle_sig_meta}; } |
    md5sum |gawk '{print $1}')
for i in '-r requirements.txt' %{py_build_extra} './'; do
    PYTHONUSERBASE='%{buildroot}/%{py_base}' \
        pip%{py_version} install \
            --user \
            --no-cache-dir \
            --progress-bar off \
            --no-index \
            --find-links "../pymod_${sig}" \
            --no-warn-script-location \
            $i
done
# remove extra modules only needed to build and install
PYTHONUSERBASE='%{buildroot}/%{py_base}' \
    pip%{py_version} uninstall -y %{py_build_extra}
cd ..

# Python wrapper with env PYTHONUSERBASE for bin scripts
echo $'#!/bin/sh\nPYTHONUSERBASE=%{py_base} exec /usr/bin/env python%{py_version} "$@"' \
    > %{buildroot}/%{py_base}/pywrap
chmod 755 %{buildroot}/%{py_base}/pywrap
sed -i -e '1i #!%{py_base}/pywrap' -e '1d' %{buildroot}/%{py_base}/bin/*
# Move gns3 scripts to system bin
mkdir -p %{buildroot}/%{_bindir}
mv %{buildroot}/%{py_base}/bin/{gns3server,gns3vmnet} %{buildroot}/%{_bindir}/

# Remove python shebang in .py files
find %{buildroot}/%{py_base}/ -name '*.py' -print \
   -exec sed -i '1{\@^#!/usr/bin/env python@d}' {} \;

# Remove empty files
find %{buildroot}/ -type f -name .gitkeep -delete

# Systemd service
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
mkdir -p  %{buildroot}%{_sharedstatedir}/gns3

%files
# gns3-server
%license %{gns3server}/LICENSE
%doc %{gns3server}/README.md %{gns3server}/CHANGELOG
%{_bindir}/{gns3server,gns3vmnet}
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
