#/bin/bash

cd /home/amour/test_media
drive pull -no-prompt RootioNew/Northern\ Uganda\ Pilot/Luo_Recordings/News 
latest_file=`ls -t /home/amour/test_media/RootioNew/Northern\ Uganda\ Pilot/Luo_Recordings/News/ | awk '{printf("%s",$0);exit}'`
cp "/home/amour/test_media/RootioNew/Northern Uganda Pilot/Luo_Recordings/News/$latest_file" /home/amour/media/news/current_news.wav
echo "============= Done syncing on `date`==============="
