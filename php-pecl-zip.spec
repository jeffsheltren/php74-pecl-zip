# spec file for php-pecl-zip
#
# Copyright (c) 2013 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%global pecl_name      zip
%global with_zts       0%{?__ztsphp:1}

Summary:      A ZIP archive management extension
Summary(fr):  Une extension de gestion des ZIP
Name:         php-pecl-zip
Version:      1.12.2
Release:      1%{?dist}
License:      PHP
Group:        Development/Languages
URL:          http://pecl.php.net/package/zip

Source:       http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires: php-devel
BuildRequires: pkgconfig(libzip) >= 0.11.1
BuildRequires: zlib-devel
BuildRequires: php-pear

Requires(post): %{_bindir}/pecl
Requires(postun): %{_bindir}/pecl
Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}

Provides:     php-pecl(%{pecl_name}) = %{version}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:     php-%{pecl_name} = %{version}-%{release}
Provides:     php-%{pecl_name}%{?_isa} = %{version}-%{release}


%description
Zip is an extension to create and read zip files.

%description -l fr
Zip est une extension pour créer et lire les archives au format ZIP.


%prep 
%setup -c -q

cd %{pecl_name}-%{version}

# delete bundled libzip to ensure it is not used (except zipint.h)
rm lib/*.c

cd ..
: Create the configuration file
cat >%{pecl_name}.ini << 'EOF'
; Enable ZIP extension module
extension=%{pecl_name}.so
EOF

%if %{with_zts}
: Duplicate sources tree for ZTS build
cp -pr %{pecl_name}-%{version} %{pecl_name}-zts
%endif


%build
cd %{pecl_name}-%{version}
%{_bindir}/phpize
%configure \
  --with-libzip \
  --with-libdir=%{_lib} \
  --with-php-config=%{_bindir}/php-config

make %{?_smp_mflags}

%if %{with_zts}
cd ../%{pecl_name}-zts
%{_bindir}/zts-phpize
%configure \
  --with-libzip \
  --with-libdir=%{_lib} \
  --with-php-config=%{_bindir}/zts-php-config

make %{?_smp_mflags}
%endif


%install
make -C %{pecl_name}-%{version} install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{pecl_name}.ini %{buildroot}%{php_inidir}/%{pecl_name}.ini

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C %{pecl_name}-zts install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{pecl_name}.ini %{buildroot}%{php_ztsinidir}/%{pecl_name}.ini
%endif

# Test & Documentation
cd %{pecl_name}-%{version}
for i in $(grep 'role="test"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
cd %{pecl_name}-%{version}
: minimal load test of NTS extension
%{_bindir}/php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}

: upstream test suite for NTS extension
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
TEST_PHP_EXECUTABLE=%{_bindir}/php \
%{_bindir}/php \
   run-tests.php

%if %{with_zts}
cd ../%{pecl_name}-zts
: minimal load test of ZTS extension
%{_bindir}/zts-php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}

: upstream test suite for ZTS extension
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
TEST_PHP_EXECUTABLE=%{_bindir}/zts-php \
%{_bindir}/zts-php \
   run-tests.php
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc %{pecl_docdir}/%{pecl_name}
%doc %{pecl_testdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml
%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Wed Oct 23 2013 Remi Collet <remi@fedoraproject.org> 1.12.2-1
- update to 1.12.2
- drop merged patches
- install doc in pecl doc_dir
- install tests in pecl test_dir

* Thu Aug 22 2013 Remi Collet <rcollet@redhat.com> 1.12.1-5
- really really fix all spurious-executable-perm

* Thu Aug 22 2013 Remi Collet <rcollet@redhat.com> 1.12.1-4
- really fix all spurious-executable-perm

* Thu Aug 22 2013 Remi Collet <rcollet@redhat.com> 1.12.1-3
- fixes from review comments #999313: clarify License
- drop execution right from sources
- BR libzip-devel always needed

* Tue Aug 20 2013 Remi Collet <rcollet@redhat.com> 1.12.1-2
- refresh our merged patches from upstream git

* Thu Aug 08 2013 Remi Collet <rcollet@redhat.com> 1.12.1-1
- New spec for version 1.12.1
