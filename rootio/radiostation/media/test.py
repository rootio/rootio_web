from community_media import CommunityMedia

comm = CommunityMedia("advertisements","1")
items = comm.get_media_files()
print items
