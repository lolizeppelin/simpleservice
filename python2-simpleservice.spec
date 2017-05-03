%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"
)}

%define proj_name GLockRedis

Name:           glockredis
Version:        1.0.0
Release:        0%{?dist}
Summary:        python glock lock base by redis
Group:          Development/Libraries
License:        MPLv1.1 or GPLv2
URL:            http://github.com/Lolizeppelin/%{proj_name}
Source0:        %{proj_name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires:  python-setuptools
Requires:       redis >= 2.10.0


%description
GLockRedis is a  glock lock base by redis


%prep
%setup -q -n %{proj_name}-%{version}

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
install -D -m 644 README.rst %{buildroot}%{_docdir}/%{name}-%{version}

%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%dir %{python_sitelib}/%{name}*
%{python_sitelib}/%{name}*/*
%doc README.rst

%changelog

* Thu Mar 7 2017 Lolizeppelin <lolizeppelin@gmail.com> - 1.0.0
- Initial Package