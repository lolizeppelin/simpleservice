%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
)}

%define proj_name simpleservice

Name:           python-%{proj_name}
Version:        1.0.0
Release:        0%{?dist}
Summary:        simpleservice copy from openstack
Group:          Development/Libraries
License:        MPLv1.1 or GPLv2
URL:            http://github.com/Lolizeppelin/%{proj_name}
Source0:        %{proj_name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-setuptools >= 11.0

Requires:       python >= 2.6.6
Requires:       python < 3.0
Requires:       python-simpleutil >= 1.0.0
Requires:       python-six >= 1.9.0
Requires:       python-eventlet >= 0.15.2

%description
simpleservice copy from openstack

%files
%defattr(-,root,root,-)
%{python_sitelib}/%{proj_name}/*
%dir %{python_sitelib}/%{proj_name}/plugin
%doc README.rst
%doc doc/*



%package wsgi
Summary:        wsgi framework for simpleservice plugin
Group:          Development/Libraries
Requires:       %{name} == %{version}
Requires:       python-webob >= 1.2.3
Requires:       python-paste
Requires:       python-paste-deploy >= 1.5.0
Requires:       python-routes >= 1.12.3
Requires:       python-routes < 2.0

%description wsgi
wsgi server framework

%files wsgi
%defattr(-,root,root,-)
%dir %{python_sitelib}/%{proj_name}/wsgi



%package rpc
Summary:        rpc framework for simpleservice plugin
Group:          Development/Libraries
Requires:       %{name} == %{version}
Requires:       python-kombu >= 3.0.25

%description rpc
rpc framework for simpleservice plugin

%files ormdb
%defattr(-,root,root,-)
%dir %{python_sitelib}/%{proj_name}/rpc




%package ormdb
Summary:        orm framework for simpleservice plugin
Group:          Development/Libraries
Requires:       %{name} == %{version}
Requires:       python-sqlalchemy >= 1.0.11

%description ormdb
orm framework for simpleservice plugin

%files ormdb
%defattr(-,root,root,-)
%dir %{python_sitelib}/%{proj_name}/ormdb



%prep
%setup -q -n %{proj_name}-%{version}
rm -rf %{proj_name}.egg-info

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%clean
%{__rm} -rf %{buildroot}


%changelog

* Mon Aug 29 2017 Lolizeppelin <lolizeppelin@gmail.com> - 1.0.0
- Initial Package