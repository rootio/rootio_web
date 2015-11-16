#/bin/sh

python pm_live_sync.py

cd /home/amour/test_media/RootioNew/Northern\ Uganda\ Pilot/PM\ Live/
pwd
latest_africa_file=`ls -t  | awk '{printf("%s",$0);exit}'`
cp $latest_africa_file /home/amour/media/pm_live/current.mp3

echo "============= Done syncing PM Live on `date`==============="
