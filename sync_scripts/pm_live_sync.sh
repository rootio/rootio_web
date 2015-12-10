#/bin/bash
cd /home/amour/RootIO_Web_Old/rootio/radiostation/sync_scripts
source /home/amour/venv/bin/activate
python pm_live_sync.py

cd /home/amour/test_media/RootioNew/Northern\ Uganda\ Pilot/PM\ Live/
pwd
latest_africa_file=`ls -t  | awk '{printf("%s",$0);exit}'`
cp $latest_africa_file /home/amour/media/pm_live/current.mp3

echo "============= Done syncing PM Live on `date`==============="
