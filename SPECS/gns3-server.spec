# https://src.fedoraproject.org/rpms/gns3-server/raw/b4f03e373ec4b6dff8323a6e2b376bc8d18f05e4/f/gns3-server.spec

# For pre-release
%global git_tag %{version}

# Filter auto-generated deps from bundled shell script (which depends on busybox only)
%global __requires_exclude_from ^%{python3_sitelib}/gns3server/compute/docker/resources/.*$

Name:           gns3-server
Version:        2.2.29
Release:        1%{?dist}
Summary:        Graphical Network Simulator 3

License:        GPLv3
URL:            http://gns3.com
Source0:        https://github.com/GNS3/gns3-server/archive/v%{git_tag}/%{name}-%{git_tag}.tar.gz
Source1:        gns3.service
Patch0:         0001-changing-busybox-udhcpc-script-path.patch

BuildArch:      noarch

BuildRequires:  git-core
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%{?systemd_requires}
BuildRequires: systemd
BuildRequires: python3-sphinx
BuildRequires: busybox
BuildRequires: make

Requires: busybox
%if 0%{?fedora} || 0%{?rhel} > 7
Recommends: docker
Recommends: qemu-kvm
%else
Requires: docker
Requires: qemu-kvm
%endif
Requires: ubridge >= 0.9.14

Provides: bundled(busybox)


%description
GNS3 is a graphical network simulator that allows you to design complex network
topologies. You may run simulations or configure devices ranging from simple
workstations to powerful routers.

This is the server package which provides an HTTP REST API for the client (GUI).

%package doc
Summary: Documentation for %{name}
Requires: %{name} = %{version}-%{release}
%description doc
%{name}-doc package contains documentation.


%prep
%autosetup -S git -n %{name}-%{git_tag}

# Relax requirements
sed -i -r 's/==/>=/g' requirements.txt
sed -i -r 's/3.7.4.*/3.7.4/' requirements.txt
sed -i -r 's/psutil>=5.8.0/psutil>=5.7.0/' requirements.txt
sed -i -r 's/sentry-sdk.*//g' requirements.txt


%build
%py3_build

%install
%py3_install

# Remove shebang
find %{buildroot}/%{python3_sitelib}/ -name '*.py' -print \
   -exec sed -i '1{\@^#!/usr/bin/env python@d}' {} \;
# Remove empty file
rm -f %{buildroot}/%{python3_sitelib}/gns3server/symbols/.gitkeep

# Build the doc1834283s
%{make_build} -C docs html
/bin/rm -f docs/_build/html/.buildinfo

## Systemd service part
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
mkdir -p  %{buildroot}%{_sharedstatedir}/gns3

## Remove tests: they are outside the namespace
rm -rf %{buildroot}/%{python3_sitelib}/tests/

## Don't bundle busybox with the package.
rm -f %{buildroot}/%{python3_sitelib}/gns3server/compute/docker/resources/bin/busybox

%check


%files
%license LICENSE
%doc README.rst AUTHORS CHANGELOG
%{python3_sitelib}/gns3_server*.egg-info/
%ghost %{python3_sitelib}/gns3server/compute/docker/resources/bin/busybox
%{python3_sitelib}/gns3server/
%{_bindir}/gns3server
%{_bindir}/gns3vmnet
%{_bindir}/gns3loopback
%{_unitdir}/gns3.service
%dir %attr(0755,gns3,gns3) %{_sharedstatedir}/gns3

%files doc
%license LICENSE
%doc docs/_build/html

%pre
getent group gns3 >/dev/null || groupadd -r gns3
getent passwd gns3 >/dev/null || \
       useradd -r -g gns3 -d /var/lib/gns3 -s /sbin/nologin \
               -c "gns3 server" gns3
exit 0

%post
[ -d "/var/lib/gns3" ] && chown -R gns3:gns3 %{_sharedstatedir}/gns3
%systemd_post gns3.service

# Replace bundled busybox with Fedora one
cp -f %{_sbindir}/busybox %{python3_sitelib}/gns3server/compute/docker/resources/bin/busybox

%preun
%systemd_preun gns3.service

%postun
%systemd_postun_with_restart gns3.service
