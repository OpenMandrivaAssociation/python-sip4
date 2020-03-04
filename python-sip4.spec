# extracted from sip.h, SIP_API_MAJOR_NR SIP_API_MINOR_NR defines
%define sip_api_major 11
%define sip_api_minor 1
%define sip_api       %{sip_api_major}.%{sip_api_minor}

%define _disable_ld_no_undefined 1

%ifarch aarch64
%define _disable_lto 1
%endif

Summary:	Old version of the SIP Python bindings generator
Name:		python-sip4
Version:	4.19.21
Release:	1
Group:		Development/Python
License:	GPLv2+
Url:		http://www.riverbankcomputing.co.uk/software/sip/intro
Source0:	https://www.riverbankcomputing.com/static/Downloads/sip/%{version}/sip-%{version}.tar.gz
Source1:	python-sip4.rpmlintrc
Source10:	sip-wrapper.sh
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(python2)
Obsoletes:	sip < %{version}
Obsoletes:	sip-devel < %{version}
Provides:	sip-api(%{sip_api_major}) = %{sip_api}
# make install should not strip (by default), kills -debuginfo
Patch50:	sip-4.18-no_strip.patch
# Avoid hardcoding sip.so (needed for wxpython's siplib.so)
Patch53:	sip-4.19.18-no_hardcode_sip_so.patch

%description
SIP is a tool that makes it very easy to create Python bindings
for C and C++ libraries. It was originally developed to create PyQt,
the Python bindings for the Qt toolkit, but can be used to
create bindings for any C or C++ library.

%files
%{_bindir}/sip
%{py_platsitedir}/s*
%{py_platsitedir}/__pycache__/*
%{py_incdir}/sip.h
%{_sysconfdir}/rpm/macros.d/sip.macros

#------------------------------------------------------------
%package -n python-sip4-qt5
Summary:	Riverbanks' python sip Qt5
Conflicts:	%{name} < 1:4.19.17-2

%description -n python-sip4-qt5
Python sip bindings for Qt5.

%files -n python-sip4-qt5
%{py_platsitedir}/PyQt5*

#------------------------------------------------------------
%package -n python2-sip4
Summary:	Riverbanks' python sip

%description -n python2-sip4
SIP is a tool that makes it very easy to create Python bindings
for C and C++ libraries. It was originally developed to create PyQt,
the Python bindings for the Qt toolkit, but can be used to
create bindings for any C or C++ library.

%files -n python2-sip4
%{_bindir}/python2-sip
%{py2_platsitedir}/s*
%{py2_incdir}/sip.h


#------------------------------------------------------------
%package -n python2-sip4-qt5
Summary:	Riverbanks' python sip Qt5
Conflicts:	python2-sip < 1:4.19.17-2

%description -n python2-sip4-qt5
Python2 sip bindings for Qt5.

%files -n python2-sip4-qt5
%{py2_platsitedir}/PyQt5*

#------------------------------------------------------------
%prep
%setup -qc sip-%{version}
%autopatch -p0
mv sip-%{version} python3
for i in python2 qt5-python3 qt5-python2; do
	cp -a python3 $i
done

# Check API minor/major numbers
export real_api_major=`grep SIP_API_MAJOR_NR siplib/sip.h.in|head -n1|awk -F' ' '{print $3}'`
export real_api_minor=`grep SIP_API_MINOR_NR siplib/sip.h.in|head -n1|awk -F' ' '{print $3}'`
if [ $real_api_major -ne %{sip_api_major} ]; then
    echo 'Wrong spi major specified: Should be' $real_api_major ', but set' %{sip_api_major}
    exit 1
fi
if [ $real_api_minor -ne %{sip_api_minor} ]; then
    echo 'Wrong spi minor specified: Should be' $real_api_minor ', but set' %{sip_api_minor}
    exit 1
fi

#  Don't use X11R6 prefix for includes neither libraries by default.
for file in specs/linux-*; do
    perl -p -i -e "s@/X11R6/@/@g" $file
done

%build

for i in python3 qt5-python3 python2 qt5-python2; do
	echo $i |grep -q python2 && PY=python2 || PY=python
	echo $i |grep -q qt5 && EXT="--sip-module PyQt5.sip" || EXT=""
	pushd $i
	$PY configure.py --no-dist-info $EXT CC="%_cc" CFLAGS="%{optflags} -fPIC" CXX="%{__cxx}" LINK="%{__cxx}" LINK_SHLIB="%{__cxx}" LFLAGS="%{ldflags}"
	%make_build CC=%{__cc} CXX=%{__cxx} CFLAGS="%{optflags} -fPIC" CXXFLAGS="%{optflags} -fPIC" #LIBS="%{?ldflags} -lpython%{py3_ver}"
	popd
done

%install
for i in python2 qt5-python2 qt5-python3 python3; do
	pushd $i
	%make_install
	[ "$i" = "python2" ] && mv %{buildroot}%{_bindir}/sip %{buildroot}%{_bindir}/python2-sip
	popd
done

mkdir -p %{buildroot}%{_sysconfdir}/rpm/macros.d/
cat > %{buildroot}%{_sysconfdir}/rpm/macros.d/sip.macros << EOF
# extracted from sip.h, SIP_API_MAJOR_NR SIP_API_MINOR_NR defines
%%sip_api_major %{sip_api_major}
%%sip_api_minor %{sip_api_minor}
%%sip_api       %{sip_api_major}.%{sip_api_minor}
EOF
