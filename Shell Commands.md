# Useful Shell Commands

## Shell related:
- `ni <path/file_name.ext>`: creates an empty file (similar to touch)
- `ls "some/path/to/dir/" | grep -i <some_name>`
    - The pipe `|` sends (pipes) the output of the first command as input into the second
    - `-i`: case-insensitive search
- `find "some/path/to/dir" -(i)name "<*some_name>" -type <{f, d}>`
    - Finds files/directories matching the name
    - `-iname`: case-insensitive name match
    - `*`: wildcard to match anything
    - `-type`: `f` for files, or `d` for directories (if none, matches both)
- `gci -r -<{file, directory}> <*.ext>`
  - pwsh7 equivalent to `find`; `gci`: Get-ChildItem
  - `-r`: recursively finds matching files/directories within every subdirectory from root `.`
- `find "some/path/to/dir" -(i)name "<some_name*>" -type <{f, d}> -exec rm -r {} +`
    - `-exec ... {}` specifies the function (`rm` in this case) to run against all matched files/dirs
    - `-r`: recursively removes all matched files/dirs in **batch mode**
    - `+`: batch mode (executes after everything is fetched, all at once rather than iteratively)

## winget related:
- `winget` is Windows built-in package manager (similar to `scoop`)
- `winget list`: lists all installed packages (via winget or not)
- `winget list --name <package_name>`: lists all packages that contain that name (case-insensitive)

## Python related:
- `pip list --outdated`
    - Lists all outdated installed packages
- `pip install --no-cache-dir ...`
    - Installs fresh (non-cached wheels/files)
