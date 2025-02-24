<u>To initialize a git repository</u>:<br>
`$ git init`

<u>To check the status/changes of your git staging area</u>:<br>
`$ git status`

<u>To stage (add a file to the staging area) a file</u>:<br>
`$ git add file_name.ext`

<u>To stage all new and modified (but not deleted) files in the current working directory and its subdirectories</u>:<br>
`$ git add .`

<u>To stage all changes (modifications and deletions) made to **tracked** files (not new), but leave _untracked_ files unstaged</u>:<br>
`$ git add -u`

<u>To stage all files having the an “.ext” extension</u>:<br>
`$ git add \*.ext`

<u>To stage all changes in the entire directory (current and all its subdirectories)</u>:<br>
`$ git add -A`

<u>To stage modified files by referring to their index number as they show up in `git status`</u>:<br>
`$ git add -i`

<u>To remove a staged file from the staging area (unstage a file)</u>:<br>
`$ git reset some_file.py`

<u>To remove all files staged from the staging area</u>:<br>
`$ git reset`

<u>To print a list of all currently tracked files in your git repo</u>:<br>
`$ git ls-files`

<u>To stop tracking a file in Git while keeping it in your local directory</u>:<br>
`$ git rm --cached -r <file_name.ext>`<br>
(the `-r` option is used to *recursively* remove files in a directory, and the `—cached` option ensures that the files are only removed from the Git index, not your local file system)

<u> To set a name and email (author) for each commit globally (for all repos on machine)</u>:

    $ git config --global user.name "Your Name"
    $ git config --global user.email "youremail@example.com"

<u>To commit changes from your staging area to your _local_ repository</u>:<br>
`$ git commit -m “Some message to display with commit”`

<u>To add **and** commit all tracked files (modified or deleted) in one step</u>:<br>
`$ git commit -am “Some message to display with commit”`

<u>To optimize the local repository by cleaning up (garbage collecting) unnecessary files and optimizing the local storage of the repository data</u>:<br>
`$ git gc`

<u>To connect your local repository to a remote one via URL</u>:<br>
`$ git remote add <origin> <remote_repo_url>.git`<br>
(`origin` is an **alias** for the URL of the remote repository, such that you don't have to type it again; you can name it whatever you want)<br>
(to change the name of the alias reference: `$ git remote rename origin <new_name>`)

<u>To check if your current directory is connected to any GitHub repos remotely</u>:<br>
`$ git remote -v`<br>
(your local repo can be connected to multiple remote repositories)

<u>To download the latest changes (commits and branches) from a remote repository to your local repository just to view them</u>:<br>
`$ git fetch <origin>`

<u>To show any commits made to the remote branch but not your local branch</u>:<br>
`$ git log HEAD..origin/main`

<u>To pull the latest changes from the remote repository (to stay up to date and avoid conflicts)</u>:<br>
`$ git pull <origin> main` <==> `git fetch` followed by `git merge`

<u>If after `git pull` your local branch and remote branch have diverged, meaning they both have commits that the other doesn't have, you must reconcile</u>:<br>
`$ git pull --rebase` or if no branch is set as upstream (`-u`), then: `git pull <origin main> --rebase`<br>
(this will rebase your local changes on top of the remote changes, and will move your local commits to the tip (top) of the remote branch)

- Better to create a new branch first not to affect the main working branch, then after resolving conflicts (selecting appropriate changes from local and remote commits) and removing the conflict markers, add the resolved file(s) to the staging area and commit the merge. Finally, merge the updated branch back to your main branch via: `$ git checkout main` --> `$ git merge <new-branch>` then delete the new branch: `$ git branch -d <new-branch>`

<u>To disconnect your local repository from a remote one</u>:<br>
`$ git remote rm <origin>`

<u>To check available branches and which one are you're currently on in the repo</u>:<br>
`$ git branch`<br>

<u>To list all available remote branches (better to `git fetch` first)</u>:
`$ git branch -r`

<u>To list all local and available remote branches</u>:
`$ git branch -a`

<u>To rename a branch</u>:<br>
`$ git branch -m <old_name> <new_name>`

<u>To delete a branch that you're not currently on</u>:<br>
`$ git branch -d <branch_name>`

<u>To check which remote repo/branch is set as the upstream (being tracked) for current local branch</u>:<br>
`$ git branch -vv`<br>
(each local branch can have its own upstream)

<u>To have the current local branch track a particular remote branch (become its upstream)</u>:<br>
`$ git branch -u <upstream>/<branch_name>`

<u>To switch into a different branch (which will consequently update your CWD and its files)</u>:<br>
`$ git checkout <branch_name>`<br>
(adding the `-b` option after the `checkout` keyword in the command will create a *new* branch with that name if the branch doesn't already exist in the repo)

<u>To push all changes from your local repository to the remote repository</u>:<br>
`$ git push -u origin main`<br>
(the `-u` is there that such Git will remember that you want your **local** `main` branch to track the `main` branch from repo `origin`)<br>
(you only need to specify `-u origin main` the first time, then you can just `git push` or `pull` directly)

<u>To create a Git submodule (nested repo) within the current repo in a specified path</u>:<br>
`$ git submodule add <remote_repo_url> <path/to/subdirectory>`

<u>If you cloned a repo that contains submodules, you need to initialize and update them</u>:<br>
`$ git submodule update --init --recursive` (to be run from the root directory of the main repo)

<u>If you want to initialize submodules upon cloning a repo</u>:<br>
`$ git clone --recurse-submodules <remote_repo_url>`

<u>If submodule is a forked repo (tracks changes/updates from its original repo; **upstream**), make sure its updated</u>:<br>
`$ git checkout main` --> `$ git pull <upstream> <main>`
(after you make commits and push changes from within a submodule, you must then commit the (updated) submodule itself from the root directory 
`$ cd ..` -> `$ git commit -am 'update submodule'`)

<u>To push large files (e.g., CSV), you need to use Git LFS</u>:<br>
`$ git lfs install`

Now, if you have already committed your large file to Git:

    $ git lfs migrate import --include="path/to/large_file.csv"
    $ git push origin main  (try --force if necessary)

Otherwise:

    $ git lfs track "path/to/large_file.csv"
    $ git add .gitattributes
    $ git add path/to/large_file.csv
    $ git commit -m "Add a new large CSV file"
    $ git push origin main
