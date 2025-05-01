default:
	@just --list

download url destination:
	@echo 'Downloading {{url}} to {{destination}}...'
	uv run main.py --loglevel debug "{{url}}" "{{destination}}"
