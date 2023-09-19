#!/bin/bash

BUILDNAME=base
DATE=$(date +%m-%d-%y_%H-%M)
IMGDIR=$(pwd)/${BUILDNAME}-image_${DATE}
CONTAINERSUPPORT=$(which docker) || $(which podman)
PKGMANAGER=$(which yum) || $(which dnf)

color () {
	if [ "$2" == "yellow" ] ; then
		clr="33"
	elif [ "$2" == "green" ] ; then
		clr="32"
	else
		clr="0m"
	fi

	SCLR="\033[0;1;${clr}m"
	ECLR="\033[0m"
	printf '%b\n' "${SCLR}${1}${ECLR}"
}

color "Building Image Directory..." "yellow"
/usr/bin/mkdir -p ${IMGDIR} >&2>/dev/null && color "OK!" "green" || exit 1

color "Installing Baseline Linux Requirements..." "yellow"
${PKGMANAGER} install --releasever 8 --installroot ${IMGDIR} -y basesystem filesystem binutils >&2>/dev/null && color "OK!" "green" || exit 1

color "Cleaning Up ${IMGDIR}..." "yellow"
/usr/bin/rm -rf ${IMGDIR}/var/cache/dnf ${IMGDIR}/var/log/* ${IMGDIR}/usr/locale/locale/archive >&2>/dev/null && color "OK!" "green" || exit 1

color "Building Image Tarball..." "yellow"
/usr/bin/tar -czvf ${IMGDIR}.tar -C ${IMGDIR} . >&2>/dev/null && color "OK!" "green" || exit 1

color "Loading Tarball Into Docker..." "yellow"
/usr/bin/cat ${IMGDIR}.tar | ${CONTAINERSUPPORT} import - ${BUILDNAME}:${DATE} >&2>/dev/null && color "OK!" "green" || exit 1

color "Saving Docker Image..." "yellow"
${CONTAINERSUPPORT} save localhost/${BUILDNAME}:${DATE} -o ${BUILDNAME}-${DATE}.tar.gz >&2>/dev/null && color "OK!" "green" || exit 1

color "Removing Artifacts..." "yellow"
/usr/bin/rm -rf ${IMGDIR}.tar >&2>/dev/null && color "${IMGDIR}.tar OK!" "green" || exit 1
/usr/bin/rm -rf ${IMGDIR} >&2>/dev/null && color "${IMGDIR} OK!" "green" || exit 1
