#!/bin/sh
unset pyproject
[ -f pyproject.toml ] || { echo "pyproject.toml not found" >&2; exit 69; }
pyproject="$(xvert tj < pyproject.toml)"

print_sections() {
	local section req_file
	case $# in
		[1-9]*)
			for section
			do
				echo "${section}"
			done
			;;
	esac
	{
		echo ""
		echo "${pyproject}" | jq -r '.project."optional-dependencies" | to_entries[] | .key'
		for req_file in requirements-*.txt
		do
			[ -f "${req_file}" ] || continue
			section="${req_file#requirements-}"
			echo "${section%.txt}"
		done
	} | sort -u
}

doit() {
	local section key packages req_file
	case "${section}" in
		"") key=".project.dependencies";;
		*) key=".project.\"optional-dependencies\".${section}";;
	esac
	packages="$(xvert tj < pyproject.toml | jq -r "(${key} // [])[]" | sed -n 's/[^A-Za-z0-9_-].*//p' | tr '\n' ,)"
	packages="${packages%,}"
	req_file="requirements${section:+"-${section}"}.txt"
	echo "${section:-"<default>"} -> ${packages:-"(none)"}"
	case "${packages}" in
		"") rm -f "${req_file}";;
		*) pipdeptree -j -p "${packages}" | jq -r '.[] | .package, .dependencies[] | .package_name + "==" + .installed_version' | sort -u > "${req_file}";;
	esac
}

print_sections |
while read -r section
do
	doit "${section}"
done
