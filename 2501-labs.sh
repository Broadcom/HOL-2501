NOW=$(date "+%Y.%m.%d-%H.%M.%S")
GIT_LABS=/vpodrepo/2025-labs/2501/labfiles

rm -rf $GIT_LABS
bash ~holuser/hol/Tools/proxyfilteroff.sh

git clone "https://github.com/vmware-aria-hol/hol-2501-lab-files.git" $GIT_LABS
bash ~holuser/hol/Tools/proxyfilteron.sh

rm -rf $GIT_LABS/.git

git add $GIT_LABS
git commit -a -m "labfiles update - $NOW"
git push

