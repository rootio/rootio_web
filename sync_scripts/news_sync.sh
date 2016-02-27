#/bin/sh

cd /home/amour/test_media
drive pull -no-prompt -ignore-conflict -ignore-name-clashes RootioNew/Northern\ Uganda\ Pilot/Luo_Recordings/News 
latest_file=`ls -t /home/amour/test_media/RootioNew/Northern\ Uganda\ Pilot/Luo_Recordings/News/ | awk '{printf("%s",$0);exit}'`
echo $latest_file
extension='${latest_file##*.}'
echo $extension
pwd
if [ $extension != 'wav' ]; then
    sox "RootioNew/Northern\ Uganda\ Pilot/Luo_Recordings/News/$latest_file" /home/amour/media/news/tmp.wav
else
    cp "/home/amour/test_media/RootioNew/Northern Uganda Pilot/Luo_Recordings/News/$latest_file" /home/amour/media/news/tmp.wav
fi

#Normalize
sox --norm /home/amour/media/news/tmp.wav /home/amour/media/news/current_news.wav

echo "============= Done syncing on `date`==============="
