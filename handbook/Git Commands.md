<u>To initialize a git repository</u>:<br>
`$git init`

<u>To check the status/changes of your git staging area</u>:<br>
`$git status`

<u>To stage (add a file to the staging area) a file</u>:<br>
`$git add file_name.ext`

<u>To stage all new and modified (but not deleted) files in the current working directory and its subdirectories</u>:<br>
`$git add .`

<u>To stage all changes (modifications and deletions) made to **tracked** files (not new), but leave _untracked_ files unstaged</u>:<br>
`$git add -u`

<u>To stage all files having an “.ext” extension</u>:<br>
`$git add \*.ext`

<u>To stage all changes in the entire directory (current and all its subdirectories)</u>:<br>
`$git add -A`

<u>To stage modified files by referring to their index number as they show up in `git status`</u>:<br>
`$git add -i`

- Note: `git stash` works similarily to `git add` but instead of staging the files, it "stashes" them temporarily such that you can pull without issues.

<u>To remove a staged file from the staging area (unstage a file)</u>:<br>
`$git reset some_file.py`

<u>To remove all files staged from the staging area</u>:<br>
`$git reset`

<u>To print a list of all currently tracked files in your git repo</u>:<br>
`$git ls-files`

<u>To stop tracking (**untrack**) a file/folder and remove it from remote repo (remove from Git index) while keeping it in your local directory</u>:<br>
`$git rm --cached -r {file_name.ext, folder_name}`<br>
(the `-r` option is used to _recursively_ remove files in a directory)<br>
(the `—cached` option ensures that the files are only removed from the Git index (staging area), not your local file system)

<u>To keep a file unchanged (frozen) in the remote repo (never push changes) while allowing local changes</u>:\
`$git update-index --assume-unchanged <file.ext>`

<u> To set a name and email (author) for each commit globally (for all repos on machine)</u>:

    $git config --global user.name "Your Name"
    $git config --global user.email "youremail@example.com"

<u>To commit changes from your staging area to your _local_ repository</u>:<br>
`$git commit -m “Some message to display with commit”`

<u>To add/stage **and** commit all _tracked_ files (modified or deleted) in one step</u>:<br>
`$git commit -am “<Some message to display with commit>”`

<u>To create annotated tags (package versions) and associate them with your commits</u>:<br>
`$git tag -a v0.1.0 -m "<some_message>"` -> `$git push --follow-tags`\
(running `git push --tags` will **only** push the tags, without the commits)

<u>To optimize the local repository by garbage collecting unnecessary files and optimizing the local storage of the repository data</u>:<br>
`$git gc`

<u>To connect your local repository to a remote one via URL</u>:<br>
`$git remote add <origin> <remote_repo_url>`<br>
(`origin` is an **alias** for the URL of the remote repository, such that you don't have to type it again; you can name it whatever you want)<br>
(to change the name of the alias reference: `$git remote rename origin <new_name>`)

<u>To check if your current directory is connected to any GitHub repos remotely</u>:<br>
`$git remote -v`<br>
(your local repo can be connected to multiple remote repositories)

<u>To download the latest changes (commits and branches) from a remote repository to your local repository just to view them</u>:<br>
`$git fetch <origin>`

<u>To show any commits made to the remote branch but not your local branch</u>:<br>
`$git log HEAD..origin/main`

<u>To create and switch to a new branch</u>:\
`$git checkout -b <branch_name>` or `$git switch -c <branch_name>`<br>
- Make sure to commit your changes on the current branch before creating/switching to a new one!

<u>To check available branches and which one are you're currently on in the repo</u>:<br>
`$git branch`

<u>To list all available remote branches (do `git fetch` first)</u>:\
`$git branch -r`

<u>To list all available local and remote branches</u>:\
`$git branch -a`

<u>To rename a branch (useful to match local repo's branch name with remote's for direct push/pull)</u>:<br>
`$git branch -m <old_name> <new_name>`

<u>To copy over all changes from a feature branch into the `main` branch:</u>
- First, you must commit your changes on the feature branch
- Checkout the `main` branch before running the merge
- `$git merge <feature-branch>`

<u>To push into a remote branch that has a different name than the current local branch</u>:<br>
`$git push <origin> <local_branch>:<remote_branch>`

<u>To delete a branch that you're not currently on</u>:<br>
`$git branch -d <branch_name>`
- Then to push the deletion to the remote rep: `git push <origin> :<branch_name>`, where `:` means *push "nothing"*

<u>To check which remote repo/branch is set as the upstream (being tracked) for current local branch</u>:<br>
`$git branch -vv`<br>
(upstream branch is used for direct push/pull, and each local branch can have its own upstream)

<u>To have the current local branch *track* a particular remote branch (become its upstream)</u>:<br>
`$git branch -u <origin>/<branch_name>`
(`-u` flag stands for `--set-upstream-to`)

<u>To switch into a different branch (which will consequently update your CWD and its files)</u>:<br>
`$git checkout <branch_name>`<br>

<u>To push all changes from your local repository to the remote repository</u>:<br>
`$git push -u origin main`<br>
(the `-u` is there that such Git will remember that you want your **local** `main` branch to track the `main` branch from repo `origin`)<br>
(you only need to specify `-u origin main` the first time, then you can just `git push` or `pull` directly)

<u>To pull the latest changes from the remote repository (to stay up to date and avoid conflicts)</u>:<br>
`$git pull <origin> main` <==> `git fetch` followed by `git merge`  (optionally `--rebase`)<br>
(rebase places local changes *on top* of the remote changes; local commits are moved to the top of the remote branch, keeping _linear_ commit history)

<u>If the local branch and remote branch have a diverged commit history (progressed independently) ==> they have commits that the other doesn't have; you must reconcile</u>:<br>
- While resolving divergence (via `rebase` or `merge`), a **conflict** might arise if both branches **modified the same line(s) in the same file**
- Before addressing the conflict (same file, different contents), your change(s) must be locally committed first.
- After you address the conflict, you stage (`add`) that file again and commit to conclude the merge.
- Better to create a new branch first not to affect the main working branch, then after resolving conflicts in the new branch (selecting appropriate changes from local and remote commits) and removing the conflict markers, add the resolved file(s) to the staging area and commit the merge. Finally, merge the updated branch back to your main branch via: `$git checkout main` --> `$git merge <new-branch>` then delete the new branch: `$git branch -d <new-branch>`

<u>To disconnect your local repository from a remote one</u>:<br>
`$git remote rm <origin>`

<u>To create a Git submodule (nested repo) within the current repo in a specified path</u>:<br>
`$git submodule add <remote_repo_url> <path/to/subdirectory>`

<u>If you cloned a repo that contains submodules, you need to initialize and update them</u>:<br>
`$git submodule update --init --recursive` (to be run from the root directory of the main repo)

<u>If you want to initialize submodules upon cloning a repo</u>:<br>
`$git clone --recurse-submodules <remote_repo_url>`

<u>If submodule is a forked repo (tracks changes/updates from its original repo; **upstream**), make sure its updated</u>:<br>
`$git checkout main` --> `$git pull <upstream> <main>`
(after you make commits and push changes from within a submodule, you must then commit the (updated) submodule itself from the root directory
`$cd ..` -> `$git commit -am 'update submodule'`)

<u>To push large files (e.g., CSV), you need to use Git LFS</u>:<br>
`$git lfs install`

Now, if you have already committed your large file to Git:

    $git lfs migrate import --include="path/to/large_file.csv"
    $git push origin main  (try --force if necessary)

Otherwise:

    $git lfs track "path/to/large_file.csv"
    $git add .gitattributes
    $git add path/to/large_file.csv
    $git commit -m "Add a new large CSV file"
    $git push origin main
