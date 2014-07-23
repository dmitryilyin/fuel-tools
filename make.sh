#!/bin/sh
dir="$(dirname ${0})"
cd "${dir}" || exit 1

make_file() {
  sed -e "/from color import Color/r color.py" -e "/from color import Color/d" "${1}" | \
  sed -e "/from cib import CIB/r cib.py" -e "/from cib import CIB/g" | \
  cat > "build/${1}"
  chmod +x "build/${1}"
}

make_file crm_ops.py
make_file color_chart.py
make_file cib_check_cgi.py
make_file haproxy-status.py
