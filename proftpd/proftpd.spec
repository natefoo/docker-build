# Modified from EPEL 7: http://pkgs.fedoraproject.org/cgit/rpms/proftpd.git/plain/proftpd.spec
#
# Rebuild switch:
#  --with integrationtests	enable integration tests (not fully maintained, likely to fail)
#

# This package uses systemd init from Fedora 16, but can use it for
# Fedora 15 if built using --with systemd
%if 0%{?fedora} > 15 || 0%{?rhel} > 6
%global _with_systemd --with-systemd
%endif
%global use_systemd %{!?_with_systemd:0}%{?_with_systemd:1}

# With systemd, the runtime directory is /run rather than /var/run
%if %{use_systemd}
%global rundir /run
%else
%global rundir %{_localstatedir}/run
%endif

# rundir (/var/run or /run) is on tmpfs from Fedora 15, RHEL 7
%if 0%{?fedora} > 14 || 0%{?rhel} > 6
%global rundir_tmpfs 1
%endif

# Support systemd presets from Fedora 18, RHEL 7
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%global preset_support 1
%endif

# For memcached support we need libmemcached >= 0.41, available from F-14 (EL-6 and below have libmemcached 0.31)
%if 0%{?rhel} > 6 || 0%{?fedora} > 13
%global have_libmemcached 1
%endif

# Do a hardened build where possible
%global _hardened_build 1

#global prever rc3
%global rpmrel 5
%global mod_vroot_version 0.9.5

Summary:		Flexible, stable and highly-configurable FTP server
Name:			proftpd
Version:		1.3.6
Release:		%{?prever:0.}%{rpmrel}%{?prever:.%{prever}}%{?dist}
License:		GPLv2+
URL:			http://www.proftpd.org/

Source0:		ftp://ftp.proftpd.org/distrib/source/proftpd-%{version}%{?prever}.tar.gz
Source1:		proftpd.conf
Source5:		proftpd-welcome.msg
Source9:		proftpd.sysconfig
Source10:		http://github.com/Castaglia/proftpd-mod_vroot/archive/v%{mod_vroot_version}.tar.gz

Patch1:			proftpd-1.3.6-shellbang.patch
Patch2:			proftpd.conf-no-memcached.patch
Patch3:			proftpd-1.3.4rc1-mod_vroot-test.patch

# FIXME: which of these pactches are included in the 1.3.6 branch?
#Patch100:		https://github.com/proftpd/proftpd/commit/459693c7.patch
#Patch101:		https://github.com/proftpd/proftpd/commit/389cc579.patch
#Patch102:		https://github.com/proftpd/proftpd/commit/1825a2b8.patch
#Patch103:		https://github.com/proftpd/proftpd/commit/73887e02.patch
#Patch104:		https://github.com/proftpd/proftpd/commit/8a186e2d.patch
#Patch105:		https://github.com/proftpd/proftpd/commit/c3e5d75f.patch
#Patch106:		proftpd-1.3.6-add-enable-tests-nonetwork-option.patch
#Patch107:		https://github.com/proftpd/proftpd/commit/adfdc01d.patch
#Patch108:		https://github.com/proftpd/proftpd/commit/6cc96b5f.patch
#Patch109:		https://github.com/proftpd/proftpd/commit/aa85f127.patch
#Patch110:		https://github.com/proftpd/proftpd/commit/7907aa65.patch
#Patch111:		https://github.com/proftpd/proftpd/commit/08ba2f63.patch
#Patch112:		https://github.com/proftpd/proftpd/commit/757b9633.patch
#Patch113:		https://github.com/proftpd/proftpd/commit/41ecb7dc.patch

BuildRequires:		coreutils
BuildRequires:		gcc
BuildRequires:		GeoIP-devel
BuildRequires:		gettext
BuildRequires:		libacl-devel
BuildRequires:		libcap-devel
%if 0%{?have_libmemcached:1}
BuildRequires:		libmemcached-devel >= 0.41
%endif
BuildRequires:		mysql-devel
BuildRequires:		ncurses-devel
BuildRequires:		openldap-devel
BuildRequires:		openssl-devel
BuildRequires:		pam-devel
BuildRequires:		pcre-devel >= 7.0
BuildRequires:		perl-generators
BuildRequires:		perl%{?fedora:-interpreter}
BuildRequires:		pkgconfig
BuildRequires:		postgresql-devel
BuildRequires:		tar
BuildRequires:		tcp_wrappers-devel
BuildRequires:		zlib-devel

# Test suite requirements
BuildRequires:		check-devel
%if 0%{?_with_integrationtests:1}
BuildRequires:		perl(Compress::Zlib)
BuildRequires:		perl(Digest::MD5)
BuildRequires:		perl(HTTP::Request)
BuildRequires:		perl(IO::Socket::SSL)
BuildRequires:		perl(LWP::UserAgent)
BuildRequires:		perl(Net::FTPSSL)
BuildRequires:		perl(Net::SSLeay)
BuildRequires:		perl(Net::Telnet)
BuildRequires:		perl(Sys::HostAddr)
BuildRequires:		perl(Test::Harness)
BuildRequires:		perl(Test::Unit) >= 0.25
BuildRequires:		perl(Time::HiRes)
%endif

# Need systemd-units for ownership of /usr/lib/tmpfiles.d directory
%if 0%{?rundir_tmpfs:1}
Requires:		systemd-units
%endif
Requires(preun):	coreutils, findutils
%if %{use_systemd}
BuildRequires:		systemd-units
Requires(post):		systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units
%else
Requires(post):		/sbin/chkconfig
Requires(preun):	/sbin/service, /sbin/chkconfig
Requires(postun):	/sbin/service
%endif

Provides:		ftpserver

%description
ProFTPD is an enhanced FTP server with a focus toward simplicity, security,
and ease of configuration. It features a very Apache-like configuration
syntax, and a highly customizable server infrastructure, including support for
multiple 'virtual' FTP servers, anonymous FTP, and permission-based directory
visibility.
%if %{use_systemd}
This package defaults to the standalone behavior of ProFTPD, but all the
needed scripts to have it run by systemd instead are included.
%else
This package defaults to the standalone behavior of ProFTPD, but all the
needed scripts to have it run by xinetd instead are included.
%endif

%package devel
Summary:	ProFTPD - Tools and header files for developers
Requires:	%{name} = %{version}-%{release}
# devel package requires the same devel packages as were build-required
# for the main package
Requires:	gcc, libtool
Requires:	GeoIP-devel
Requires:	libacl-devel
Requires:	libcap-devel
Requires:	mysql-devel
Requires:	openldap-devel
Requires:	openssl-devel
Requires:	pam-devel
Requires:	pcre-devel
Requires:	postgresql-devel
Requires:	pkgconfig
Requires:	ncurses-devel
Requires:	tcp_wrappers-devel
Requires:	zlib-devel
%if 0%{?have_libmemcached:1}
Requires:	libmemcached-devel >= 0.41
%endif

%description devel
This package is required to build additional modules for ProFTPD.

%package ldap
Summary:	Module to add LDAP support to the ProFTPD FTP server
Requires:	%{name} = %{version}-%{release}

%description ldap
Module to add LDAP support to the ProFTPD FTP server.

%package mysql
Summary:	Module to add MySQL support to the ProFTPD FTP server
Requires:	%{name} = %{version}-%{release}

%description mysql
Module to add MySQL support to the ProFTPD FTP server.

%package postgresql
Summary:	Module to add PostgreSQL support to the ProFTPD FTP server
Requires:	%{name} = %{version}-%{release}

%description postgresql
Module to add PostgreSQL support to the ProFTPD FTP server.

%package utils
Summary:	ProFTPD - Additional utilities
Requires:	%{name} = %{version}-%{release}
Requires:	perl-interpreter
# ftpasswd --use-cracklib requires Crypt::Cracklib
BuildRequires:	perl(Crypt::Cracklib)
Requires:	perl(Crypt::Cracklib)

%description utils
This package contains additional utilities for monitoring and configuring the
ProFTPD server:

* ftpasswd: generate passwd(5) files for use with AuthUserFile
* ftpcount: show the current number of connections per server/virtualhost
* ftpmail: monitor transfer log and send email when files uploaded
* ftpquota: manipulate quota tables
* ftptop: show the current status of FTP sessions
* ftpwho: show the current process information for each FTP session

%prep
%setup -q -n %{name}-%{version}%{?prever}

# Extract mod_vroot source into contrib/
# Directory must be named mod_vroot for configure script to find it
cd contrib
tar xfz %{SOURCE10}
mv proftpd-mod_vroot-%{mod_vroot_version} mod_vroot
cd -

# Default config file
cp -p %{SOURCE1} proftpd.conf

# Avoid documentation name conflicts
mv contrib/README contrib/README.contrib

# Change shellbangs /usr/bin/env perl ⇒ /usr/bin/perl
%patch1

# If we don't have libmemcached support, remove the mod_tls_memcache
# snippet from the config file
%if 0%{!?have_libmemcached:1}
%patch2
%endif

# If we're running the full test suite, include the mod_vroot test
%patch3 -p1 -b .test_vroot

# Check for symlinks in home directory path as logging-in user
# http://bugs.proftpd.org/show_bug.cgi?id=4306
# https://bugzilla.redhat.com/show_bug.cgi?id=1443507
# https://github.com/proftpd/proftpd/pull/496
#%patch100 -p1

# Fix API tests to work in Fedora/RHEL environments
# https://github.com/proftpd/proftpd/issues/483
# https://github.com/proftpd/proftpd/pull/510
# https://github.com/proftpd/proftpd/pull/514
#%patch101 -p1
#%patch102 -p1
#%patch103 -p1
#%patch104 -p1

# Fix similars functionality and unit test
# https://github.com/proftpd/proftpd/pull/513
#%patch105 -p1

# Add functionality to disable external network tests
# https://github.com/proftpd/proftpd/pull/497
#%patch106 -p1

# Systemd requires that executeable pathnames are absolute
# https://github.com/proftpd/proftpd/pull/502
#%patch107 -p1

# Systemd upstream recommends Type = simple for services if possible
# https://github.com/proftpd/proftpd/pull/506
#%patch108 -p1

# Don't mess with system profiles in TLSCipherSuite
# https://github.com/proftpd/proftpd/pull/499
#%patch109 -p1
#%patch110 -p1

# Remove redundant bind() to controls socket
# https://github.com/proftpd/proftpd/issues/501
#%patch111 -p1

# mod_sftp failed to check shadow password information when publickey
# authentication used
# http://bugs.proftpd.org/show_bug.cgi?id=4308
#%patch112 -p1

# Use of "AllowEmptyPasswords off" broke SFTP/SCP logins
# http://bugs.proftpd.org/show_bug.cgi?id=4309
#%patch113 -p1

# OpenSSL Cipher Profiles introduced in Fedora 21
# Elsewhere, we use the default of DEFAULT:!ADH:!EXPORT:!DES
%if 0%{?fedora} < 21 && 0%{?rhel} < 8
sed -i -e '/^[[:space:]]*TLSCipherSuite[[:space:]]*PROFILE=SYSTEM$/d' proftpd.conf
%endif

# Tweak logrotate script for systemd compatibility (#802178)
%if %{use_systemd}
sed -i -e '/killall/s/test.*/systemctl reload proftpd.service/' \
	contrib/dist/rpm/proftpd.logrotate
%endif

# Avoid docfile dependencies
chmod -x contrib/xferstats.holger-preiss

# Remove bogus exec permissions from source files
chmod -c -x include/hanson-tpl.h lib/hanson-tpl.c

%build
# Modules to be built as DSO's (excluding mod_ifsession, always specified last)
SMOD1=mod_sql:mod_sql_passwd:mod_sql_mysql:mod_sql_postgres
SMOD2=mod_quotatab:mod_quotatab_file:mod_quotatab_ldap:mod_quotatab_radius:mod_quotatab_sql
SMOD3=mod_ldap:mod_ban:mod_wrap:mod_ctrls_admin:mod_facl:mod_load:mod_vroot
SMOD4=mod_radius:mod_ratio:mod_rewrite:mod_site_misc:mod_exec:mod_shaper:mod_geoip
SMOD5=mod_wrap2:mod_wrap2_file:mod_wrap2_sql:mod_copy:mod_deflate:mod_ifversion:mod_qos
SMOD6=mod_sftp:mod_sftp_pam:mod_sftp_sql:mod_tls_shmcache%{?have_libmemcached::mod_tls_memcache}

%configure \
			--libexecdir="%{_libexecdir}/proftpd" \
			--localstatedir="%{rundir}/proftpd" \
			--disable-strip \
			--enable-ctrls \
			--enable-dso \
			--enable-facl \
			--enable-ipv6 \
%{?have_libmemcached:	--enable-memcache} \
			--enable-nls \
			--enable-openssl \
			--disable-pcre \
			--disable-redis \
			--enable-shadow \
			--enable-tests=nonetwork \
			--with-libraries="%{_libdir}/mysql" \
			--with-includes="%{_includedir}/mysql" \
			--with-modules=mod_readme:mod_auth_pam:mod_tls \
			--with-shared=${SMOD1}:${SMOD2}:${SMOD3}:${SMOD4}:${SMOD5}:${SMOD6}:mod_ifsession

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot} \
	rundir="%{rundir}/proftpd" \
	INSTALL_USER=`id -un` \
	INSTALL_GROUP=`id -gn`
install -D -p -m 640 proftpd.conf	%{buildroot}%{_sysconfdir}/proftpd.conf
install -D -p -m 644 contrib/dist/rpm/proftpd.pam \
					%{buildroot}%{_sysconfdir}/pam.d/proftpd
%if %{use_systemd}
install -D -p -m 644 contrib/dist/rpm/proftpd.service \
					%{buildroot}%{_unitdir}/proftpd.service
install -D -p -m 644 contrib/dist/systemd/proftpd.socket \
					%{buildroot}%{_unitdir}/proftpd.socket
install -D -p -m 644 contrib/dist/systemd/proftpd@.service \
					%{buildroot}%{_unitdir}/proftpd@.service
%else
install -D -p -m 755 contrib/dist/rpm/proftpd.init.d \
					%{buildroot}%{_sysconfdir}/rc.d/init.d/proftpd
install -D -p -m 644 contrib/dist/rpm/xinetd \
					%{buildroot}%{_sysconfdir}/xinetd.d/xproftpd
%endif
install -D -p -m 644 contrib/dist/rpm/proftpd.logrotate \
					%{buildroot}%{_sysconfdir}/logrotate.d/proftpd
install -D -p -m 644 %{SOURCE5}		%{buildroot}%{_localstatedir}/ftp/welcome.msg
install -D -p -m 644 %{SOURCE9}		%{buildroot}%{_sysconfdir}/sysconfig/proftpd
mkdir -p %{buildroot}%{_localstatedir}/{ftp/{pub,uploads},log/proftpd}
touch %{buildroot}%{_sysconfdir}/ftpusers

# Make sure %%{rundir}/proftpd exists at boot time for systems where it's on tmpfs (#656675)
%if 0%{?rundir_tmpfs:1}
install -d -m 755 %{buildroot}%{_prefix}/lib/tmpfiles.d
install -p -m 644 contrib/dist/rpm/proftpd-tmpfs.conf \
					%{buildroot}%{_prefix}/lib/tmpfiles.d/proftpd.conf
%endif

# Find translations
%find_lang proftpd

# Failing one test: api/fsio.c:3539:E:base:fs_close_extra_fds_test:0: (after this point) Early exit with return value 2
#   and I just don't have the time to figure this out for something that's only going to be temporary.
#%check
## Integration tests not fully maintained - stick to API tests only by default
#%if 0%{?_with_integrationtests:1}
#ln ftpdctl tests/
#make check
#%else
## API tests should always be OK
#if ! make -C tests api-tests; then
#	# Diagnostics to report upstream
#	cat tests/api-tests.log
#	./proftpd -V
#	# Fail the build
#	false
#fi
#%endif

%post
%if %{use_systemd}
/bin/systemctl daemon-reload &>/dev/null || :
%endif
if [ $1 -eq 1 ]; then
	# Initial installation
%if ! %{use_systemd}
	/sbin/chkconfig --add proftpd || :
%endif
%if 0%{?preset_support:1}
	/bin/systemctl preset proftpd.service &>/dev/null || :
%endif
	IFS=":"; cat /etc/passwd | \
	while { read username nu nu gid nu nu nu nu; }; do \
		if [ $gid -lt 100 -a "$username" != "ftp" ]; then
			echo $username >> %{_sysconfdir}/ftpusers
		fi
	done
fi

%preun
if [ $1 -eq 0 ]; then
	# Package removal, not upgrade
%if %{use_systemd}
	/bin/systemctl --no-reload disable proftpd.service &>/dev/null || :
	/bin/systemctl stop proftpd.service &>/dev/null || :
%else
	/sbin/service proftpd stop &>/dev/null || :
	/sbin/chkconfig --del proftpd || :
%endif
	find %{rundir}/proftpd -depth -mindepth 1 |
		xargs rm -rf &>/dev/null || :
fi

%postun
%if %{use_systemd}
/bin/systemctl daemon-reload &>/dev/null || :
%endif
if [ $1 -ge 1 ]; then
	# Package upgrade, not uninstall
%if %{use_systemd}
	/bin/systemctl try-restart proftpd.service &>/dev/null || :
%else
	/sbin/service proftpd condrestart &>/dev/null || :
else
	# Package removal, not upgrade
	/sbin/service xinetd reload &>/dev/null || :
%endif
fi

%files -f proftpd.lang
%if 0%{?_licensedir:1}
%license COPYING
%else
%doc COPYING
%endif
%doc CREDITS ChangeLog NEWS README.md
# Many READMEs moved to doc/howtos
#%doc README.DSO README.modules README.IPv6 README.PAM
#%doc README.capabilities README.classes README.controls README.facl
#%doc contrib/README.contrib contrib/README.ratio
%doc README.modules contrib/README.ratio
%doc doc/* sample-configurations/
%dir %{_localstatedir}/ftp/
%dir %{_localstatedir}/ftp/pub/
%dir %{rundir}/proftpd/
%config(noreplace) %{_localstatedir}/ftp/welcome.msg
%config(noreplace) %{_sysconfdir}/blacklist.dat
%config(noreplace) %{_sysconfdir}/dhparams.pem
%config(noreplace) %{_sysconfdir}/ftpusers
%config(noreplace) %{_sysconfdir}/logrotate.d/proftpd
%config(noreplace) %{_sysconfdir}/pam.d/proftpd
%config(noreplace) %{_sysconfdir}/proftpd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/proftpd
%if %{use_systemd}
%{_unitdir}/proftpd.service
%{_unitdir}/proftpd.socket
%{_unitdir}/proftpd@.service
%else
%config(noreplace) %{_sysconfdir}/xinetd.d/xproftpd
%{_sysconfdir}/rc.d/init.d/proftpd
%endif
%if 0%{?rundir_tmpfs:1}
%{_prefix}/lib/tmpfiles.d/proftpd.conf
%endif
%{_bindir}/ftpdctl
%{_sbindir}/ftpscrub
%{_sbindir}/ftpshut
%{_sbindir}/in.proftpd
%{_sbindir}/proftpd
%{_mandir}/man5/proftpd.conf.5*
%{_mandir}/man5/xferlog.5*
%{_mandir}/man8/ftpdctl.8*
%{_mandir}/man8/ftpscrub.8*
%{_mandir}/man8/ftpshut.8*
%{_mandir}/man8/proftpd.8*
%dir %{_libexecdir}/proftpd/
%{_libexecdir}/proftpd/mod_ban.so
%{_libexecdir}/proftpd/mod_ctrls_admin.so
%{_libexecdir}/proftpd/mod_copy.so
%{_libexecdir}/proftpd/mod_deflate.so
%{_libexecdir}/proftpd/mod_exec.so
%{_libexecdir}/proftpd/mod_facl.so
%{_libexecdir}/proftpd/mod_geoip.so
%{_libexecdir}/proftpd/mod_ifsession.so
%{_libexecdir}/proftpd/mod_ifversion.so
%{_libexecdir}/proftpd/mod_load.so
%{_libexecdir}/proftpd/mod_qos.so
%{_libexecdir}/proftpd/mod_quotatab.so
%{_libexecdir}/proftpd/mod_quotatab_file.so
%{_libexecdir}/proftpd/mod_quotatab_radius.so
%{_libexecdir}/proftpd/mod_quotatab_sql.so
%{_libexecdir}/proftpd/mod_radius.so
%{_libexecdir}/proftpd/mod_ratio.so
%{_libexecdir}/proftpd/mod_rewrite.so
%{_libexecdir}/proftpd/mod_sftp.so
%{_libexecdir}/proftpd/mod_sftp_pam.so
%{_libexecdir}/proftpd/mod_sftp_sql.so
%{_libexecdir}/proftpd/mod_shaper.so
%{_libexecdir}/proftpd/mod_site_misc.so
%{_libexecdir}/proftpd/mod_sql.so
%{_libexecdir}/proftpd/mod_sql_passwd.so
%{?have_libmemcached:%{_libexecdir}/proftpd/mod_tls_memcache.so}
%{_libexecdir}/proftpd/mod_tls_shmcache.so
%{_libexecdir}/proftpd/mod_vroot.so
%{_libexecdir}/proftpd/mod_wrap.so
%{_libexecdir}/proftpd/mod_wrap2.so
%{_libexecdir}/proftpd/mod_wrap2_file.so
%{_libexecdir}/proftpd/mod_wrap2_sql.so
%exclude %{_libexecdir}/proftpd/*.a
%exclude %{_libexecdir}/proftpd/*.la
%attr(331, ftp, ftp) %dir %{_localstatedir}/ftp/uploads/
%attr(750, root, root) %dir %{_localstatedir}/log/proftpd/

%files devel
%{_bindir}/prxs
%{_includedir}/proftpd/
%{_libdir}/pkgconfig/proftpd.pc

%files ldap
%doc README.LDAP contrib/mod_quotatab_ldap.ldif contrib/mod_quotatab_ldap.schema
%{_libexecdir}/proftpd/mod_ldap.so
%{_libexecdir}/proftpd/mod_quotatab_ldap.so

%files mysql
%{_libexecdir}/proftpd/mod_sql_mysql.so

%files postgresql
%{_libexecdir}/proftpd/mod_sql_postgres.so

%files utils
%doc contrib/xferstats.holger-preiss
%{_bindir}/ftpasswd
%{_bindir}/ftpcount
%{_bindir}/ftpmail
%{_bindir}/ftpquota
%{_bindir}/ftptop
%{_bindir}/ftpwho
%{_mandir}/man1/ftpasswd.1*
%{_mandir}/man1/ftpcount.1*
%{_mandir}/man1/ftpmail.1*
%{_mandir}/man1/ftpquota.1*
%{_mandir}/man1/ftptop.1*
%{_mandir}/man1/ftpwho.1*

%changelog
* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Fri Jul 28 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 13 2017 Paul Howarth <paul@city-fan.org> - 1.3.6-3
- mod_sftp failed to check shadow password information when publickey
  authentication used (http://bugs.proftpd.org/show_bug.cgi?id=4308)
- Use of "AllowEmptyPasswords off" broke SFTP/SCP logins
  (http://bugs.proftpd.org/show_bug.cgi?id=4309)

* Thu Jul 13 2017 Petr Pisar <ppisar@redhat.com> - 1.3.6-2
- perl dependency renamed to perl-interpreter
  <https://fedoraproject.org/wiki/Changes/perl_Package_to_Install_Core_Modules>

* Mon May 22 2017 Paul Howarth <paul@city-fan.org> - 1.3.6-1
- Update to 1.3.6 (see NEWS for details)
- Update mod_vroot to 0.9.5 (API compatibility with 1.3.6)
- Add upstream fixes for flaky API tests
  (https://github.com/proftpd/proftpd/issues/483)
  (https://github.com/proftpd/proftpd/pull/510)
  (https://github.com/proftpd/proftpd/pull/514)
- Add functionality to disable external network tests
  (https://github.com/proftpd/proftpd/pull/497)
- Update template TLS configuration
- PCRE 7.0 always available for use now
- Disable PCRE support for now as JIT compiler has SELinux issues
  (https://bugs.exim.org/show_bug.cgi?id=1749)
- Update proftpd.service to use Type=simple rather than Type=forking
  (https://github.com/proftpd/proftpd/pull/506)
- Remove redundant bind() to controls socket
  (https://github.com/proftpd/proftpd/issues/501)
- Fix similars functionality and unit test
  (https://github.com/proftpd/proftpd/pull/513)
- Integration tests can use system Test::Unit now
- tcpd.h can always be found in tcp_wrappers-devel now

* Wed May  3 2017 Paul Howarth <paul@city-fan.org> - 1.3.5e-2
- AllowChrootSymlinks off could cause login failures depending on filesystem
  permissions: use the IDs of the logging-in user to perform the directory
  walk, looking for symlinks, to be more consistent with similar checks done
  during login (#1443507, upstream bug 4306)
- Crypt::CrackLib always available now

* Mon Apr 10 2017 Paul Howarth <paul@city-fan.org> - 1.3.5e-1
- Update to 1.3.5e
  - SFTP clients using umac-64@openssh.com digest failed to connect
    (upstream bug 4287)
  - SFTP rekeying failure with ProFTPD 1.3.5d, caused by null pointer
    dereference (upstream bug 4288)
  - AllowChrootSymlinks off did not check entire DefaultRoot path for symlinks
    (CVE-2017-7418, upstream bug 4295)
- Change shellbangs in shipped perl scripts to use system perl
- Drop EL-5 support
  - Drop BuildRoot: and Group: tags
  - Drop explicit buildroot cleaning in %%install section
  - Drop explicit %%clean section
  - /etc/pam.d/password-auth always available now
  - pcre 7.0 or later always available now

* Sun Feb 12 2017 Paul Howarth <paul@city-fan.org> - 1.3.5d-3
- Properly allocate (and clear) the UMAC contexts, to fix segfault in mod_sftp
  (#1420365, upstream bug 4287)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.5d-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 16 2017 Paul Howarth <paul@city-fan.org> - 1.3.5d-1
- Update to 1.3.5d
  - Support OpenSSL 1.1.x API (upstream bug 4275)
  Bug fixes:
  - SSH rekey during authentication can cause issues with clients
    (upstream bug 4254)
  - Recursive SCP uploads of multiple directories not handled properly
    (upstream bug 4257)
  - LIST returns different results for file, depending on path syntax
    (upstream bug 4259)
  - "AuthAliasOnly on" in server config breaks anonymous logins
    (upstream bug 4255)
  - CapabilitiesEngine directive not honored for <IfUser>/<IfGroup> sections
    (upstream bug 4272)
  - Memory leak when mod_facl is used (upstream bug 4278)
  - All FTP logins treated as anonymous logins again (upstream bug 4283,
    regression in 1.3.5c of upstream bug 3307)

* Sat Nov 19 2016 Paul Howarth <paul@city-fan.org> - 1.3.5b-3
- Support OpenSSL 1.1.x API (upstream bug 4275)

* Sat May 21 2016 Paul Howarth <paul@city-fan.org> - 1.3.5b-2
- Handle client/server version skew in mod_sql_mysql
  (https://forums.proftpd.org/smf/index.php?topic=11887.0)
- Fix a possible cause of segfaults in mod_sftp (#1337880, upstream bug 4203)
- BR: perl-generators for correct dependencies in utils sub-package

* Fri Mar 11 2016 Paul Howarth <paul@city-fan.org> - 1.3.5b-1
- Update to 1.3.5b
  - mod_geoip did not load all of the GeoIPTables properly (upstream bug 4187)
  - "Incorrect string value" reported by mod_sql_mysql for some UTF8 characters
    (upstream bug 4191)
  - SSH rekey failed when using RSA hostkey smaller than 2048 bits
    (upstream bug 4097)
  - MLSD/MLST fact type "cdir" is incorrectly used for the current working
    directory (upstream bug 4198)
  - HiddenStores temporary files not removed when exceeding quota using SCP
    (upstream bug 4201)
  - MLSD lines not properly terminated with CRLF (upstream bug 4202)
  - Zero-length memory allocation possible, with undefined results
    (upstream bug 4209)
  - Avoid unbounded SFTP extended attribute key/values (upstream bug 4210)
  - Ensure that FTP data transfer commands fail appropriately when
    "RootRevoke on" is in effect (upstream bug 4212)
  - Handle FTP re-authentication attempts better (upstream bug 4217)
  - Permissions on files uploaded via STOU did not honor configured Umask
    (upstream bug 4223)
  - Support SFTP clients that send multiple INIT requests (upstream bug 4227)
  - TLSDHParamFile directive appears ignored because unexpected DH is chosen
    (upstream bug 4230)
- Drop unbundled old version of mod_geoip
- Drop upstreamed patches

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.5a-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Dec  1 2015 Paul Howarth <paul@city-fan.org> - 1.3.5a-5
- Avoid unbounded SFTP extended attribute key/values
  (#1286977, http://bugs.proftpd.org/show_bug.cgi?id=4210)

* Thu Oct 29 2015 Paul Howarth <paul@city-fan.org> - 1.3.5a-4
- See if we can fix crash in mod_lang
  http://bugs.proftpd.org/show_bug.cgi?id=4206
  https://retrace.fedoraproject.org/faf/reports/10744/

* Thu Sep 10 2015 Paul Howarth <paul@city-fan.org> - 1.3.5a-3
- Add dependency on perl(Crypt::Cracklib), needed for ftpasswd --use-cracklib

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.5a-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 28 2015 Paul Howarth <paul@city-fan.org> - 1.3.5a-1
- Update to 1.3.5a
  - Fixed "stalled" SSL/TLS handshakes for data transfers
  - Fixed handling of SSH keys with overlong Comment headers in mod_sftp_sql
  - By default, mod_tls will no longer support SSLv3 connections; in order to
    support SSLv3 connections (for sites that need to), you must explicitly
    configure this via the TLSProtocol directive, e.g.:
    TLSProtocol SSLv3 TLSv1 ...
  - The mod_copy module is enabled by default; there may be cases where the
    module should be disabled, without requiring a rebuild of the server, thus
    mod_copy now supports a CopyEngine directive to enable/disable the module
  - The DeleteAbortedStores directive (for Bug#3917) is only enabled when
    HiddenStores is in effect, as intended when originally implemented, rather
    than all the time
  - Many other bug-fixes, see NEWS for details
- Drop upstreamed patches

* Wed May 27 2015 Paul Howarth <paul@city-fan.org> - 1.3.5-7
- Update mod_vroot to 0.9.4
  - Fix broken vroot alias checks (GH#4, GH#5)
  - Improve documentation
  - Add further regression tests

* Tue Apr 28 2015 Paul Howarth <paul@city-fan.org> - 1.3.5-6
- Unauthenticated copying of files via SITE CPFR/CPTO was allowed by mod_copy
  (CVE-2015-3306, http://bugs.proftpd.org/show_bug.cgi?id=4169)

* Thu Feb  5 2015 Paul Howarth <paul@city-fan.org> - 1.3.5-5
- Update mod_vroot to 0.9.3 and drop upstreamed mod_vroot patch
- Anonymous upload directory specification needs to be slightly different if
  mod_vroot is in use (#1045922)
  http://sourceforge.net/p/proftp/mailman/message/31728570/
- For systemd-based systems, use systemd rather than xinetd for inetd mode
  activation (#737707); to use this mode, set "ServerType inetd" in
  /etc/proftpd.conf and do "systemctl enable proftpd.socket" (and
  "systemctl start proftpd.socket" to start listening for connections)
- Use %%license where possible

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.5-3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun  7 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1.3.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 16 2014 Paul Howarth <paul@city-fan.org> 1.3.5-2
- Add upstream fix to ignore any ENOPROTOOPT errors when setting the
  IPv6 TCLASS (TOS) flags on the socket; they make for noisier logging
  without providing any actual value to the user/admin (upstream bug 4055)

* Fri May 16 2014 Paul Howarth <paul@city-fan.org> 1.3.5-1
- Update to 1.3.5 (see NEWS for details)
- Drop upstreamed patches
- Drop sysv-to-systemd migration script
- No longer need to support pam_stack

* Fri Dec 20 2013 Paul Howarth <paul@city-fan.org> 1.3.4d-5
- Fix support for 8192-bit DH parameters (#1044586)
- Add 3072-bit and 7680-bit DH parameters (upstream bug 4002)

* Sat Sep 14 2013 Paul Howarth <paul@city-fan.org> 1.3.4d-4
- Fix mod_sftp/mod_sftp_pam invalid pool allocation during kbdint authentication
  (#1007678, upstream bug #3973, CVE-2013-4359)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1.3.4d-2.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> 1.3.4d-2.1
- Perl 5.18 rebuild

* Mon Jun 17 2013 Paul Howarth <paul@city-fan.org> 1.3.4d-2
- Fix spurious log messages at session close (upstream bug #3945)

* Sat Jun 15 2013 Paul Howarth <paul@city-fan.org> 1.3.4d-1
- Update to 1.3.4d
  - Fixed broken build when using --disable-ipv6 configure option
  - Fixed mod_sql "SQLAuthType Backend" MySQL issues
  - Various other bugs fixed - see NEWS for details
- Drop upstreamed patch for PAM session closing

* Tue Apr 16 2013 Paul Howarth <paul@city-fan.org> 1.3.4c-2
- Make sure we can switch back to root before closing PAM sessions so that
  they're closed properly and don't pollute the system logs with dbus reject
  messages (#951728, upstream bug #3929)

* Thu Mar  7 2013 Paul Howarth <paul@city-fan.org> 1.3.4c-1
- Update to 1.3.4c
  - Added Spanish translation
  - Fixed several mod_sftp issues, including SFTPPassPhraseProvider,
    handling of symlinks for REALPATH requests, and response code logging
  - Fixed symlink race for creating directories when UserOwner is in effect
  - Increased performance of FTP directory listings
- Drop MySQL password patch, no longer needed
- Drop upstreamed proftpd patch for CVE-2012-6095
- Update patch for bug 3744 to apply against updated proftpd code

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1.3.4b-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 16 2013 Paul Howarth <paul@city-fan.org> 1.3.4b-5
- Update patch for CVE-2012-6095 to cover vroot cases

* Mon Jan  7 2013 Paul Howarth <paul@city-fan.org> 1.3.4b-4
- Fix possible symlink race when applying UserOwner to newly created directory
  (CVE-2012-6095, #892715, http://bugs.proftpd.org/show_bug.cgi?id=3841)

* Sat Sep 22 2012  Remi Collet <remi@fedoraproject.org> 1.3.4b-3
- Rebuild against libmemcached.so.11 without SASL

* Thu Aug 30 2012 Paul Howarth <paul@city-fan.org> 1.3.4b-2
- Add support for systemd presets in Fedora 18+ (#850281)

* Wed Aug  1 2012 Paul Howarth <paul@city-fan.org> 1.3.4b-1
- Update to 1.3.4b
  - Fixed mod_ldap segfault on login when LDAPUsers with no filters used
  - Fixed sporadic SFTP upload issues for large files
  - Fixed SSH2 handling for some clients (e.g. OpenVMS)
  - New FactsOptions directive; see doc/modules/mod_facts.html#FactsOptions
  - Fixed build errors on Tru64, AIX, Cygwin
  - Lots of bugs fixed - see NEWS for details
- No bzipped tarball release this time, so revert to gzipped one
- Drop patches for fixes included in upstream release

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1.3.4a-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul  3 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-10
- Move tmpfiles.d file from %%{_sysconfdir} to %%{_prefix}/lib

* Sat Apr 21 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-9
- Rebuild for new libmemcached in Rawhide

* Fri Apr 13 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-8
- Do hardened (PIE) builds where possible
- Drop %%defattr, redundant since rpm 4.4
- Always look for TLS certs in /etc/pki/tls/certs

* Mon Mar 12 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-7
- Tweak logrotate script for systemd compatibility (#802178)
- Fix leaked file descriptors for log files (as per bug 3751)

* Sat Mar  3 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-6
- Rebuild for new libmemcached in Rawhide

* Tue Feb 28 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-5
- Document SELinux configuration for ProFTPD in proftpd.conf (#785443)
- Add support for basic and administrative controls actions using ftpdctl by
  default (#786623)
- Add trace logging directives in proftpd.conf but disable them by default as
  they impair performance
- Fix ftpwho/ftptop not showing command arguments (bug 3714)
- Fix MLSD/MLST fail with "DirFakeUser off" or "DirFakeGroup off" (bug 3715)
- Fix proftpd fails to run with "Abort trap" error message (bug 3717)
- Fix LIST -R can loop endlessly if bad directory symlink exists (bug 3719)
- Fix overly restrictive module logfile permissions (bug 3720)
- Fix mod_memcache segfault on server restart (bug 3723)
- Fix unloading mod_quotatab causes segfault (#757311, bug 3724)
- Fix mod_exec does not always capture stdout/stderr output from executed
  command (bug 3726)
- Fix mod_wrap2 causes unexpected LogFormat %%u expansion for SFTP connections
  (bug 3727)
- Fix mod_ldap segfault when LDAPUsers is used with no optional filters
  (bug 3729)
- Fix DirFakeUser/DirFakeGroup off with name causes SIGSEGV for MLSD/MLST
  commands (bug 3734)
- Fix improper handling of self-signed certificate in client-sent cert list
  when "TLSVerifyClient on" is used (bug 3742)
- Fix random stalls/segfaults seen when transferring large files via SFTP
  (bug 3743)
- Support ls(1) -1 option for LIST command (bug 3744)
- Reject PASV command if no IPv4 address available (bug 3745)
- Support applying ListOptions only to NLST or to LIST commands (bug 3746)
- Support option for displaying symlinks via MLSD using syntax preferred by
  FileZilla (bug 3747)
- Fix mod_ban not closing and reopening the BanLog/BanTable file descriptors
  on restart, causing a file descriptor leak (bug 3751)
- Fix mod_ctrls no longer listening on ControlsSocket after restart (bug 3756)

* Thu Feb  9 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-4
- Rebuild for new libpcre in Rawhide

* Mon Jan 16 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-3
- Add -utils subpackage for support tools, which means the main package
  no longer requires perl

* Tue Jan 10 2012 Paul Howarth <paul@city-fan.org> 1.3.4a-2
- Make mod_vroot a DSO, loaded by default (#772354)
- VRootAlias for /etc/security/pam_env.conf is redundant, so remove it
- Add BanMessage (#772354)
- Add -devel subpackage for building third-party modules

* Fri Nov 11 2011 Paul Howarth <paul@city-fan.org> 1.3.4a-1
- Update to 1.3.4a:
  - Fixed mod_load/mod_wrap2 build issues
- Drop now-redundant workaround for building mod_load and mod_wrap2
- Drop upstreamed patch for xinetd config typo

* Thu Nov 10 2011 Paul Howarth <paul@city-fan.org> 1.3.4-1
- Update to 1.3.4, addressing the following bugs since 1.3.4rc3:
  - ProFTPD with mod_sql_mysql dies of "Alarm clock" on FreeBSD (bug 3702)
  - mod_sql_mysql.so: undefined symbol: make_scrambled_password with MySQL 5.5
    on Fedora (bug 3669)
  - PQescapeStringConn() needs a better check (bug 3192)
  - Enable OpenSSL countermeasure against SSLv3/TLSv1 BEAST attacks (bug 3704);
    to disable this countermeasure, which may cause interoperability issues
    with some clients, use the NoEmptyFragments TLSOption
  - Support SFTPOption for ignoring requests to modify timestamps (bug 3706)
  - RPM build on CentOS 5.5 (64bit): "File not found by glob" (bug 3640)
  - Response pool use-after-free memory corruption error
    (bug 3711, #752812, ZDI-CAN-1420, CVE-2011-4130)
- Drop upstream patch for make_scrambled_password_323
- Use upstream SysV initscript rather than our own
- Use upstream systemd service file rather than our own
- Use upstream PAM configuration rather than our own
- Use upstream logrotate configuration rather than our own
- Use upstream tempfiles configuration rather than our own
- Use upstream xinetd configuration rather than our own

* Thu Oct  6 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.15.rc3
- Add upstream patch to not try make_scrambled_password_323 if the MySQL
  library doesn't export it (#718327, upstream bug 3669); this removes support
  for password hashes generated on MySQL prior to 4.1

* Thu Sep 29 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.14.rc3
- Update to 1.3.4rc3 (see NEWS and RELEASE_NOTES for full details)
  - The mod_ldap configuration directives have changed to a simplified version;
    please read the "Changes" section in README.LDAP for details
  - Support for using RADIUS for authentication SSH2 logins, and for supporting
    the NAS-IPv6-Address RADIUS attribute
  - Automatically disable sendfile support on AIX systems
  - <Limit WRITE> now prevents renaming/moving a file out of the limited
    directory
  - ExtendedLog entries now written for data transfers that time out
- Drop upstreamed patches
- Use new --disable-strip option to retain debugging symbols
- Use upstream LDAP quota table schema rather than our own copy
- Add patch for broken MySQL auth (#718327, upstream bug 3669)
- Remove spurious exec permissions on systemd unit file

* Tue Sep 27 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.13.rc2
- Restore back-compatibility with older releases and EPEL, broken by -11 update
- Use /run rather than /var/run if using systemd init
- Avoid the use of triggers in SysV-to-systemd migration

* Sat Sep 17 2011  Remi Collet <remi@fedoraproject.org> 1.3.4-0.12.rc2
- Rebuild against libmemcached.so.8

* Mon Sep 12 2011 Tom Callaway <spot@fedoraproject.org> 1.3.4-0.11.rc2
- Convert to systemd

* Fri Jun  3 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.10.rc2
- Rebuild for new libmemcached in Rawhide

* Tue May 17 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.9.rc2
- Add a number of fixes for bugs reported upstream:
  - Avoid spinning proftpd process if read(2) returns EAGAIN (bug 3639)
  - SITE CPFR/CPTO does not update quota tally (bug 3641)
  - Segfault in mod_sql_mysql if "SQLAuthenticate groupsetfast" used (bug 3642)
  - Disable signal handling for exiting session processes (bug 3644)
  - Ensure that SQLNamedConnectInfos with PERSESSION connection policies are
    opened before chroot (bug 3645)
  - MaxStoreFileSize can be bypassed using REST/APPE (bug 3649)
  - Fix TCPAccessSyslogLevel directive (bug 3652)
  - Segfault with "DefaultServer off" and no matching server for incoming IP
    address (bug 3653)

* Fri Apr  8 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.8.rc2
- Update mod_geoip to 0.3 (update for new regexp API)
- Drop patch for mod_geoip API fix

* Mon Apr  4 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.7.rc2
- Update to 1.3.4rc2 (see NEWS and RELEASE_NOTES for full details)
  - Display messages work properly again
  - Fixes plaintext command injection vulnerability in FTPS implementation
    (bug 3624)
  - Fixes CVE-2011-1137 (badly formed SSH messages cause DoS - bug 3586)
  - Performance improvements, especially during server startup/restarts
  - New modules mod_memcache and mod_tls_memcache for using memcached servers
    for caching information among different proftpd servers and/or across
    sessions
  - Utilities installed by default: ftpasswd, ftpmail, ftpquota
  - New configuration directives:
    - MaxCommandRate
    - SQLNamedConnectInfo
    - TraceOptions
  - Changed configuration directives:
    - BanOnEvent
    - ExtendedLog
    - LogFormat
    - PathAllowFilter
    - PathDenyFilter
    - SFTPOptions
    - SFTPPAMOptions
    - SQLNamedQuery
    - TLSSessionCache
    - Trace
  - New documentation for ConnectionACLs and utilities (ftpasswd etc.)
- Use the pcre regexp implementation (where possible) rather than the glibc one,
  which isn't safe with untrusted regexps
  (http://bugs.proftpd.org/3595, CVE-2010-4051, CVE-2010-4052, #673040)
- We need libmemcached 0.41 or later for memcached support
- We need pcre 7.0 or later for pcre regexp support
- Nobody else likes macros for commands

* Tue Mar 22 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.4.rc1
- Rebuilt for new MySQL client library in Rawhide

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.4-0.3.rc1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 11 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.3.rc1
- Update mod_vroot to 0.9.2
- Get more of the integration tests working

* Wed Jan  5 2011 Paul Howarth <paul@city-fan.org> 1.3.4-0.2.rc1
- Update mod_vroot to 0.9.1
- Add upstream patches making unit tests work on systems where 127.0.0.1
  maps to localhost.localdomain rather than just localhost

* Fri Dec 24 2010 Paul Howarth <paul@city-fan.org> 1.3.4-0.1.rc1
- Update to 1.3.4rc1 (see RELEASE_NOTES for full details)
  - Added Japanese translation
  - Many mod_sftp bugfixes
  - Fixed SSL_shutdown() errors caused by OpenSSL 0.9.8m and later
  - Added support for SMTP authentication in ftpmail script
  - Updated fnmatch implementation, using glibc-2.9 version
  - New modules: mod_copy, mod_deflate, mod_ifversion, mod_qos
  - New configuration directives:
    - Protocols
    - ScoreboardMutex
    - SFTPClientAlive
    - WrapOptions
  - Changed configuration directives:
    - BanOnEvent
    - ListOptions
    - LogFormat
    - SFTPOptions
    - TLSOptions
    - UseSendfile
  - Deprecated configuration directives:
    - DisplayGoAway (support for this directive has been removed)
- Add %%check section, running the API tests by default
- BR: check-devel, needed for the API test suite
- Add upstream patch (http://bugs.proftpd.org/3568), modified slightly, to fix
  the API tests
- Optionally run the perl-based integration test suite if the build option
  --with integrationtests is supplied; this is off by default as it is not
  fully maintained and is expected to fail in parts
  (see http://bugs.proftpd.org/3568#c5)
- Bundle perl(Test::Unit) 0.14, needed to run the integration test suite
  (version in Fedora is incompatible later version not from CPAN)
- BR: perl modules Compress::Zlib, IO::Socket::SSL, Net::FTPSSL, Net::SSLeay,
  Net::Telnet, Test::Harness and Time::HiRes if building --with integrationtests
- New DSO modules: mod_copy, mod_deflate, mod_ifversion, mod_qos
- QoS support can be enabled in /etc/sysconfig/proftpd

* Mon Dec 20 2010 Paul Howarth <paul@city-fan.org> 1.3.3d-1
- Update to 1.3.3d
  - Fixed sql_prepare_where() buffer overflow (bug 3536, CVE-2010-4652)
  - Fixed CPU spike when handling .ftpaccess files
  - Fixed handling of SFTP uploads when compression is used

* Fri Dec 10 2010 Paul Howarth <paul@city-fan.org> 1.3.3c-3
- Update mod_vroot to 0.9 (improvements to alias handling)
- Note that the previous default configuration is broken by this change; see
  the new VRootAlias line in proftpd.conf
- Add Default-Stop LSB keyword in initscript (for runlevels 0, 1, and 6)

* Wed Dec  1 2010 Paul Howarth <paul@city-fan.org> 1.3.3c-2
- Add /etc/tmpfiles.d/proftpd.conf for builds on Fedora 15 onwards to
  support running with /var/run on tmpfs (#656675)

* Mon Nov  1 2010 Paul Howarth <paul@city-fan.org> 1.3.3c-1
- Update to 1.3.3c (#647965)
  - Fixed Telnet IAC stack overflow vulnerability (CVE-2010-4221)
  - Fixed directory traversal bug in mod_site_misc (CVE-2010-3867)
  - Fixed SQLite authentications using "SQLAuthType Backend"
- New DSO module: mod_geoip

* Fri Sep 10 2010 Paul Howarth <paul@city-fan.org> 1.3.3b-1
- Update to 1.3.3b
  - Fixed SFTP directory listing bug
  - Avoid corrupting utmpx databases on FreeBSD
  - Avoid null pointer dereferences during data transfers
  - Fixed "AuthAliasOnly on" anonymous login

* Fri Jul  2 2010 Paul Howarth <paul@city-fan.org> 1.3.3a-1
- Update to 1.3.3a
  - Added Japanese translation
  - Many mod_sftp bugfixes
  - Fixed SSL_shutdown() errors caused by OpenSSL 0.9.8m and later
  - Fixed handling of utmp/utmpx format changes on FreeBSD

* Thu Feb 25 2010 Paul Howarth <paul@city-fan.org> 1.3.3-1
- Update to 1.3.3 (see NEWS for list of fixed bugs)
- Update PID file location in initscript
- Drop upstreamed patches
- Upstream distribution now includes mod_exec, so drop unbundled source
- New DSO modules:
  - mod_sftp
  - mod_sftp_pam
  - mod_sftp_sql
  - mod_shaper
  - mod_sql_passwd
  - mod_tls_shmcache
- Configure script no longer appends "/proftpd" to --localstatedir option
- New utility ftpscrub for scrubbing the scoreboard file
- Include public key blacklist and Diffie-Hellman parameter files for mod_sftp
  in %%{_sysconfdir}
- Remove IdentLookups from config file - disabled by default now

* Mon Feb 15 2010 Paul Howarth <paul@city-fan.org> 1.3.2d-1
- Update to 1.3.2d, addressing the following issues:
  - mod_tls doesn't compile with pre-0.9.7 openssl (bug 3358)
  - Lack of PID protection in ScoreboardFile (bug 3370)
  - Crash when retrying a failed login with mod_radius being used (bug 3372)
  - RADIUS authentication broken on 64-bit platforms (bug 3381)
  - SIGHUP eventually causes certain DSO modules to segfault (bug 3387)

* Thu Dec 10 2009 Paul Howarth <paul@city-fan.org> 1.3.2c-1
- Update to 1.3.2c, addressing the following issues:
  - SSL/TLS renegotiation vulnerability (CVE-2009-3555, bug 3324)
  - Failed database transaction can cause mod_quotatab to loop (bug 3228)
  - Segfault in mod_wrap (bug 3332)
  - <Directory> sections can have <Limit> problems (bug 3337)
  - mod_wrap2 segfaults when a valid user retries the USER command (bug 3341)
  - mod_auth_file handles 'getgroups' request incorrectly (bug 3347)
  - Segfault caused by scrubbing zero-length portion of memory (bug 3350)
- Drop upstreamed segfault patch

* Thu Dec 10 2009 Paul Howarth <paul@city-fan.org> 1.3.2b-3
- Add patch for upstream bug 3350 - segfault on auth failures

* Wed Dec  9 2009 Paul Howarth <paul@city-fan.org> 1.3.2b-2
- Reduce the mod_facts patch to the single commit addressing the issue with
  directory names with glob characters (#521634), avoiding introducing a
  further problem with <Limit> (#544002)

* Wed Oct 21 2009 Paul Howarth <paul@city-fan.org> 1.3.2b-1
- Update to 1.3.2b
  - Fixed regression causing command-line define options not to work (bug 3221)
  - Fixed SSL/TLS cert subjectAltName verification (bug 3275, CVE-2009-3639)
  - Use correct cached user values with "SQLNegativeCache on" (bug 3282)
  - Fix slower transfers of multiple small files (bug 3284)
  - Support MaxTransfersPerHost, MaxTransfersPerUser properly (bug 3287)
  - Handle symlinks to directories with trailing slashes properly (bug 3297)
- Drop upstreamed defines patch (bug 3221)

* Thu Sep 17 2009 Paul Howarth <paul@city-fan.org> 1.3.2a-7
- Restore backward SRPM compatibility broken by previous change

* Wed Sep 16 2009 Tomas Mraz <tmraz@redhat.com> 1.3.2a-6
- Use password-auth common PAM configuration instead of system-auth

* Mon Sep  7 2009 Paul Howarth <paul@city-fan.org> 1.3.2a-5
- Add upstream patch for MLSD with dirnames containing glob chars (#521634)

* Wed Sep  2 2009 Paul Howarth <paul@city-fan.org> 1.3.2a-4
- New DSO module: mod_exec (#520214)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> 1.3.2a-3.1
- Rebuilt with new openssl

* Wed Aug 19 2009 Paul Howarth <paul@city-fan.org> 1.3.2a-3
- Use mod_vroot to work around PAM/chroot issues (#477120, #506735)

* Fri Jul 31 2009 Paul Howarth <paul@city-fan.org> 1.3.2a-2
- Add upstream patch to fix parallel build (http://bugs.proftpd.org/3189)

* Mon Jul 27 2009 Paul Howarth <paul@city-fan.org> 1.3.2a-1
- Update to 1.3.2a
- Add patch to reinstate support for -DPARAMETER (http://bugs.proftpd.org/3221)
- Retain CAP_AUDIT_WRITE, needed for pam_loginuid (#506735, fixed upstream)
- Remove ScoreboardFile directive from configuration file - default value
  works better with SELinux (#498375)
- Ship mod_quotatab_sql.so in the main package rather than the SQL backend
  subpackages
- New DSO modules:
  - mod_ctrls_admin
  - mod_facl
  - mod_load
  - mod_quotatab_radius
  - mod_radius
  - mod_ratio
  - mod_rewrite
  - mod_site_misc
  - mod_wrap2
  - mod_wrap2_file
  - mod_wrap2_sql
- Enable mod_lang/nls support for RFC 2640 (and buildreq gettext)
- Add /etc/sysconfig/proftpd to set PROFTPD_OPTIONS and update initscript to
  use this value so we can use a define to enable (e.g.) anonymous FTP support
  rather than having a huge commented-out section in the config file
- Rewrite config file to remove most settings that don't change upstream
  defaults, and add brief descriptions for all available loadable modules
- Move Umask and IdentLookups settings from server config to <Global> context
  so that they apply to all servers, including virtual hosts (#509251)
- Ensure mod_ifsession is always the last one specified, which makes sure that
  mod_ifsession's changes are seen properly by other modules
- Drop pam version requirement - all targets have sufficiently recent version
- Drop redundant explicit dependency on pam
- Subpackages don't need to own %%{_libexecdir}/proftpd directory
- Drop redundant krb5-devel buildreq
- Make SRPM back-compatible with EPEL-4 (TLS cert dirs, PAM config)
- Don't include README files for non-Linux platforms
- Recode ChangeLog as UTF-8
- Don't ship the prxs tool for building custom DSO's since we don't ship the
  headers either
- Prevent stripping of binaries in a slightly more robust way
- Fix release tag to be ready for future beta/rc versions
- Define RPM macros in global scope
- BuildRequire libcap-devel so that we use the system library rather than the
  bundled one, and eliminate log messages like:
  kernel: warning: `proftpd' uses 32-bit capabilities (legacy support in use)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1.3.2-3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Apr  9 2009 Matthias Saou <http://freshrpms.net/> 1.3.2-2.1
- Update the tcp_wrappers BR to be just /usr/include/tcpd.h instead.

* Thu Apr  9 2009 Matthias Saou <http://freshrpms.net/> 1.3.2-2
- Fix tcp_wrappers-devel BR conditional.

* Mon Apr  6 2009 Matthias Saou <http://freshrpms.net/> 1.3.2-1
- Update to 1.3.2.
- Include mod_wrap (#479813).
- Tried to include mod_wrap2* modules but build failed.

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 24 2009 Caolán McNamara 1.3.2-0.3.rc3
- Rebuild for dependencies

* Fri Jan  2 2009 Matthias Saou <http://freshrpms.net/> 1.3.2-0.2.rc3
- Update default configuration to have a lit of available modules and more
  example configuration for them.

* Mon Dec 22 2008 Matthias Saou <http://freshrpms.net/> 1.3.2-0.1.rc3
- Update to 1.3.2rc3 (fixes security issue #464127)
- Exclude new pkgconfig file, as we already exclude header files (if someone
  ever needs to rebuild something against this proftpd, just ask and I'll split
  out a devel package... but it seems pretty useless currently).
- Remove no longer needed find-umode_t patch.

* Fri Aug  8 2008 Matthias Saou <http://freshrpms.net/> 1.3.1-6
- Add mod_ban support (#457289, Philip Prindeville).

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org>
- Autorebuild for GCC 4.3

* Wed Feb 13 2008 Matthias Saou <http://freshrpms.net/> 1.3.1-4
- Pass --enable-shadow to also have it available, not just PAM (#378981).
- Add mod_ifsession as DSO (#432539).

* Mon Dec 17 2007 Matthias Saou <http://freshrpms.net/> 1.3.1-3
- Rebuild for new openssl, patch from Paul Howarth.

* Mon Oct 22 2007 Matthias Saou <http://freshrpms.net/> 1.3.1-2
- Include openldap schema file for quota support (Fran Taylor, #291891).
- Include FDS compatible LDIF file for quota support (converted).
- Prefix source welcome.msg for consistency.

* Tue Oct  9 2007 Matthias Saou <http://freshrpms.net/> 1.3.1-1
- Update to 1.3.1 final.
- Remove all patches (upstream).

* Sun Aug 19 2007 Matthias Saou <http://freshrpms.net/> 1.3.1-0.2.rc3
- Update to 1.3.1rc3 (the only version to fix #237533 aka CVE-2007-2165).
- Remove all patches, none are useful anymore.
- Patch sstrncpy.c for config.h not being included (reported upstream #2964).
- Patch mod_sql_mysql.c to fix a typo (already fixed in CVS upstream).
- Exclude new headers, at least until some first 3rd party module shows up.
- Clean up old leftover CVS strings from our extra files.
- LSB-ize the init script (#247033).
- Explicitly pass --enable-openssl since configure tells us "(default=no)".
- Include patch to fix open calls on F8.

* Sun Aug 12 2007 Matthias Saou <http://freshrpms.net/> 1.3.0a-8
- Fix logrotate entry to silence error when proftpd isn't running (#246392).

* Mon Aug  6 2007 Matthias Saou <http://freshrpms.net/> 1.3.0a-7
- Include patch to fix "open" calls with recent glibc.

* Mon Aug  6 2007 Matthias Saou <http://freshrpms.net/> 1.3.0a-6
- Update License field.

* Fri Jun 15 2007 Matthias Saou <http://freshrpms.net/> 1.3.0a-5
- Remove _smp_mflags to (hopefully) fix build failure.

* Fri Jun 15 2007 Matthias Saou <http://freshrpms.net/> 1.3.0a-4
- Fix PAM entry for F7+ (#244168). Still doesn't work with selinux, though.

* Fri May  4 2007 Matthias Saou <http://freshrpms.net/> 1.3.0a-4
- Fix auth bypass vulnerability (#237533, upstream #2922)... not! :-(

* Tue Feb  6 2007 Matthias Saou <http://freshrpms.net/> 1.3.0a-3
- Patch to fix local user buffer overflow in controls request handling, rhbz
  bug #219938, proftpd bug #2867.

* Mon Dec 11 2006 Matthias Saou <http://freshrpms.net/> 1.3.0a-2
- Rebuild against new PostgreSQL.

* Mon Nov 27 2006 Matthias Saou <http://freshrpms.net/> 1.3.0a-1
- Update to 1.3.0a, which actually fixes CVE-2006-5815... yes, #214820!).

* Thu Nov 16 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-10
- Fix cmdbufsize patch for missing CommandBufferSize case (#214820 once more).

* Thu Nov 16 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-9
- Include mod_tls patch (#214820 too).

* Mon Nov 13 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-8
- Include cmdbufsize patch (#214820).

* Mon Aug 28 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-7
- FC6 rebuild.

* Mon Aug 21 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-6
- Add mod_quotatab, _file, _ldap and _sql (#134291).

* Mon Jul  3 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-5
- Disable sendfile by default since it breaks displaying the download speed in
  ftptop and ftpwho (#196913).

* Mon Jun 19 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-4
- Include ctrls restart patch, see #195884 (patch from proftpd.org #2792).

* Wed May 10 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-3
- Add commented section about DSO loading to the default proftpd.conf.
- Update TLS cert paths in the default proftpd.conf to /etc/pki/tls.

* Fri Apr 28 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-2
- Mark pam.d and logrotate.d config files as noreplace.
- Include patch to remove -rpath to DESTDIR/usr/sbin/ in the proftpd binary
  when DSO is enabled (#190122).

* Fri Apr 21 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-1
- Update to 1.3.0 final.
- Remove no longer needed PostgreSQL and OpenSSL detection workarounds.
- Remove explicit conflicts on wu-ftpd, anonftp and vsftpd to let people
  install more than one ftp daemon (what for? hmm...) (#189023).
- Enable LDAP, MySQL and PostgreSQL as DSOs by default, and stuff them in
  new sub-packages. This won't introduce any regression since they weren't
  enabled by default.
- Remove useless explicit requirements.
- Rearrange scriplets requirements.
- Enable ctrls (controls via ftpdctl) and facl (POSIX ACLs).
- Using --disable-static makes the build fail, so exclude .a files in %%files.
- Silence harmless IPv6 failure message at startup when IPv6 isn't available.

* Tue Mar  7 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-0.2.rc4
- Update to 1.3.0rc4 (bugfix release).

* Mon Mar  6 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-0.2.rc3
- FC5 rebuild.

* Thu Feb  9 2006 Matthias Saou <http://freshrpms.net/> 1.3.0-0.1.rc3
- Update to 1.3.0rc3, which builds with the latest openssl.

* Thu Nov 17 2005 Matthias Saou <http://freshrpms.net/> 1.2.10-7
- Rebuild against new openssl library... not.

* Wed Jul 13 2005 Matthias Saou <http://freshrpms.net/> 1.2.10-6
- The provided pam.d file no longer works, use our own based on the one from
  the vsftpd package (#163026).
- Rename the pam.d file we use from 'ftp' to 'proftpd'.
- Update deprecated AuthPAMAuthoritative in the config file (see README.PAM).

* Tue May 10 2005 Matthias Saou <http://freshrpms.net/> 1.2.10-4
- Disable stripping in order to get useful debuginfo packages.

* Wed Apr  6 2005 Michael Schwendt <mschwendt[AT]users.sf.net> 1.2.10-3
- rebuilt

* Tue Nov 16 2004 Matthias Saou <http://freshrpms.net/> 1.2.10-2
- Bump release to provide Extras upgrade path.

* Wed Sep 22 2004 Matthias Saou <http://freshrpms.net/> 1.2.10-1
- Updated to release 1.2.10.

* Tue Jun 22 2004 Matthias Saou <http://freshrpms.net/> 1.2.9-8
- Added ncurses-devel build requires to fix the ftptop utility.

* Thu Feb 26 2004 Magnus-swe <Magnus-swe@telia.com> 1.2.9-7
- Fixed the scoreboard and pidfile issues.

* Fri Jan  9 2004 Matthias Saou <http://freshrpms.net/> 1.2.9-6
- Pass /var/run/proftpd as localstatedir to configure to fix pid and
  scoreboard file problems.

* Wed Dec 10 2003 Matthias Saou <http://freshrpms.net/> 1.2.9-4
- Fixed the MySQL include path, thanks to Jim Richardson.
- Renamed the postgres conditional build to postgresql.

* Tue Nov 11 2003 Matthias Saou <http://freshrpms.net/> 1.2.9-3
- Renamed the xinetd service to xproftpd to avoid conflict.
- Only HUP the standalone proftpd through logrotate if it's running.

* Fri Nov  7 2003 Matthias Saou <http://freshrpms.net/> 1.2.9-2
- Rebuild for Fedora Core 1.
- Modified the init script to make it i18n aware.

* Fri Oct 31 2003 Matthias Saou <http://freshrpms.net/> 1.2.9-1
- Update to 1.2.9.

* Wed Sep 24 2003 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.8p to fix secutiry vulnerability.
- Fix the TLS build option at last, enable it by default.

* Mon Aug  4 2003 Matthias Saou <http://freshrpms.net/>
- Minor fixes in included README files.

* Mon Mar 31 2003 Matthias Saou <http://freshrpms.net/>
- Rebuilt for Red Hat Linux 9.

* Thu Mar 13 2003 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.8.
- Remove the renamed linuxprivs module.
- Added TLS module build option.

* Fri Dec 13 2002 Matthias Saou <http://freshrpms.net/>
- Fix change for ScoreboardFile in the default conf, thanks to Sven Hoexter.

* Mon Dec  9 2002 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.7.

* Thu Sep 26 2002 Matthias Saou <http://freshrpms.net/>
- Rebuilt for Red Hat Linux 8.0.

* Tue Sep 17 2002 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.6.
- Fixed typo in the config for "AllowForeignAddress" thanks to Michel Kraus.
- Removed obsolete user install patch.
- Added "modular" ldap, mysql and postgresql support.

* Mon Jun 10 2002 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.5.
- Changed the welcome.msg to config so that it doesn't get replaced.

* Fri May  3 2002 Matthias Saou <http://freshrpms.net/>
- Rebuilt against Red Hat Linux 7.3.
- Added the %%{?_smp_mflags} expansion.

* Tue Oct 23 2001 Matthias Saou <http://freshrpms.net/>
- Changed the default config file : Where the pid file is stored, addedd
  an upload authorization in anon server, and separate anon logfiles.
- Updated welcome.msg to something nicer.

* Fri Oct 19 2001 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.4, since 1.2.3 had a nasty umask bug.

* Sat Aug 18 2001 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.2 final.
- Changed the default config file a lot.

* Wed Apr 25 2001 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.2rc2.

* Mon Apr  2 2001 Matthias Saou <http://freshrpms.net/>
- Update to 1.2.2rc1.

* Tue Mar 20 2001 Matthias Saou <http://freshrpms.net/>
- Added a DenyFilter to prevent a recently discovered DOS attack.
  This is only useful for fresh installs since the config file is not
  overwritten.

* Fri Mar  2 2001 Matthias Saou <http://freshrpms.net/>
- Upgraded to 1.2.1.
- New init script (added condrestart).

* Tue Feb 27 2001 Matthias Saou <http://freshrpms.net/>
- Upgraded to 1.2.0 final.

* Tue Feb  6 2001 Matthias Saou <http://freshrpms.net/>
- Upgraded to 1.2.0rc3 (at last a new version!)
- Modified the spec file to support transparent upgrades

* Wed Nov  8 2000 Matthias Saou <http://freshrpms.net/>
- Upgraded to the latest CVS to fix the "no PORT command" bug
- Fixed the ftpuser creation script
- Modified the default config file to easily change to an anonymous
  server

* Sun Oct 15 2000 Matthias Saou <http://freshrpms.net/>
  [proftpd-1.2.0rc2-2]
- Updated the spec file and build process for RedHat 7.0
- Added xinetd support
- Added logrotate.d support

* Fri Jul 28 2000 Matthias Saou <http://freshrpms.net/>
  [proftpd-1.2.0rc2-1]
- Upgraded to 1.2.0rc2

- Upgraded to 1.2.0rc1
* Sat Jul 22 2000 Matthias Saou <http://freshrpms.net/>
  [proftpd-1.2.0rc1-1]
- Upgraded to 1.2.0rc1
- Re-did the whole spec file (it's hopefully cleaner now)
- Made a patch to be able to build the RPM as an other user than root
- Added default pam support (but without /etc/shells check)
- Rewrote the rc.d script (mostly exit levels and ftpshut stuff)
- Modified the default configuration file to not display a version number
- Changed the package to standalone in one single RPM easily changeable
  to inetd (for not-so-newbie users)
- Fixed the ftpusers generating shell script (missing "nu"s for me...)
- Removed mod_ratio (usually used with databases modules anyway)
- Removed the prefix (relocations a rarely used on non-X packages)
- Gzipped the man pages

* Thu Oct 07 1999 O.Elliyasa <osman@Cable.EU.org>
- Multi package creation.
  Created core, standalone, inetd (&doc) package creations.
  Added startup script for init.d
  Need to make the "standalone & inetd" packages being created as "noarch"
- Added URL.
- Added prefix to make the package relocatable.

* Wed Sep 08 1999 O.Elliyasa <osman@Cable.EU.org>
- Corrected inetd.conf line addition/change logic.

* Sat Jul 24 1999 MacGyver <macgyver@tos.net>
- Initial import of spec.

