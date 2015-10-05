#/bin/sh
cd /home/vagrant/rootio/rootio_flexget
source venv/bin/activate
flexget -c config.yml execute

#Focus on Africa
latest_africa_file=`ls -t /home/amour/test_media/RootioNew/Northern\ Uganda\ Pilot/BBC\ Podcasts/Focus\ On\ Africa/ | awk '{printf("%s",$0);exit}'`
cp "/home/amour/test_media/RootioNew/Northern Uganda Pilot/BBC Podcasts/Focus On Africa/$latest_africa_file" /home/amour/media/bbc/latest_africa.mp3

#World News
latest_world_news_file=`ls -t /home/amour/test_media/RootioNew/Northern\ Uganda\ Pilot/BBC\ Podcasts/World\ News/ | awk '{printf("%s",$0);exit}'`
cp "/home/amour/test_media/RootioNew/Northern Uganda Pilot/BBC Podcasts/World News/$latest_world_news_file" /home/amour/media/bbc/latest_world_news.mp3

echo "============= Done syncing BBC on `date`==============="

