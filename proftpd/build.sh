#!/bin/bash
set -e

mod_vroot_version='0.9.5'
mod_vroot_src="https://codeload.github.com/Castaglia/proftpd-mod_vroot/tar.gz/v${mod_vroot_version}"
proftpd_version='1.3.6'
proftpd_src="ftp://ftp.proftpd.org/distrib/source/proftpd-${proftpd_version}.tar.gz"
rpm_source_url_base="http://pkgs.fedoraproject.org/cgit/rpms/proftpd.git/plain"
rpm_source_files="
    proftpd.conf
    proftpd-welcome.msg
    proftpd.sysconfig
    proftpd.conf-no-memcached.patch
"

host_source_files="
    proftpd-1.3.6-shellbang.patch
    proftpd-1.3.4rc1-mod_vroot-test.patch
"

su - build -c "mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS"
su - build -c "curl -L -o ~/rpmbuild/SOURCES/v${mod_vroot_version}.tar.gz $mod_vroot_src"
su - build -c "curl -o ~/rpmbuild/SOURCES/proftpd-${proftpd_version}.tar.gz $proftpd_src"
for f in $rpm_source_files; do
    su - build -c "curl -L -o ~/rpmbuild/SOURCES/$f ${rpm_source_url_base}/${f}"
done
su - build -c "cp /host/proftpd.spec ~/rpmbuild/SPECS"
for f in $host_source_files; do
    su - build -c "cp /host/$f ~/rpmbuild/SOURCES/$f"
done

yum-builddep -y ~build/rpmbuild/SPECS/proftpd.spec
su - build -c "rpmbuild -ba ~/rpmbuild/SPECS/proftpd.spec"

rsync -av ~build/rpmbuild/SRPMS /host
rsync -av ~build/rpmbuild/RPMS /host

if [ -n "${CHOWN_UID}" ]; then
    chown -Rh ${CHOWN_UID}:${CHOWN_GID:-0} /host/SRPMS /host/RPMS
fi
