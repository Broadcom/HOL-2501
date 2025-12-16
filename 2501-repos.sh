NOW=$(date "+%Y.%m.%d-%H.%M.%S")
GIT_REPOS=/vpodrepo/2025-labs/2501/gitlab

rm -rf $GIT_REPOS
bash ~holuser/hol/Tools/proxyfilteroff.sh
git clone "https://github.com/vmware-aria-hol/hol-2501-repo-files.git" $GIT_REPOS
bash ~holuser/hol/Tools/proxyfilteron.sh

rm -rf $GIT_REPOS/.git

git add $GIT_REPOS
git commit -a -m "gitlab repo update - $NOW"
git push

rm -rf $GIT_REPOS/.git
