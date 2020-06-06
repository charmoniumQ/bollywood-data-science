#!/bin/bash

cd "$(dirname "${0}")/.."

package=bollywood_data_science
src="./${package}"
check=$([ "${1}" = "check" ] && echo "true" || echo "")

function capture() {
	local log=$(mktemp)
	local command=("${@}")

	"${command[@]}" &> "${log}"
	local command_exit="${?}"

	if [ -s "${log}" -o "${command_exit}" -ne 0 ]; then
		if [ "${command_exit}" -eq 0 ]; then
			echo -e "\033[32;1m\$ ${command[@]}\033[0m"
			cat "${log}"
		else
			echo -e "\033[31;1m\$ ${command[@]}\033[0m"
			cat "${log}"
			echo -e "\033[31;1mexitted ${command_exit}\033[0m"
			exit "${command_exit}"
		fi
	fi
}

# Auto formatting

capture \
	poetry run \
		autoflake --recursive $([ -n "${check}" ] && echo "--check" || echo "--in-place") "${src}" tests

capture \
	poetry run \
		isort --recursive $([ -n "${check}" ] && echo "--check-only") "${src}" tests

capture \
	poetry run \
		black --quiet --target-version py38 $([ -n "${check}" ] && echo "--check") "${src}" tests

# Linting (formatting/style tests)

capture \
	poetry run \
		sh -c "pylint ${src} tests || poetry run pylint-exit -efail ${?}"

# Static analysis

# capture \
# 	poetry run \
# 		env PYTHONPATH="src:${PYTHONPATH}" \
# 			bandit --recursive src

capture \
	poetry run \
		env PYTHONPATH="$(dirname "${src}"):${PYTHONPATH}" \
			dmypy run -- tests

# Unit tests

capture \
	poetry run \
		pytest --quiet --cov="${src}" --cov=tests --cov-report=term-missing --exitfirst
