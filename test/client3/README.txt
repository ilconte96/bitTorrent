#Per Creare Un Nuovo File Torrent Eseguire Il Comando Di Seguito

python3 torrent_file_creator.py --input_file_path largeT.txt --torrent_file_name example.torrent --tracker_ip 127.0.0.1 --tracker_port 6881 --piece_length 256000

#Per avviare un peer leecher (il file scaricato verrà creato nello stesso path in cui si trova il client)

python3 main.py --torrent_file_path example.torrent

#Per avviare un peer seeder (il file da caricare deve trovarsi nello stesso path in cui si trova il client)

python3 main.py --torrent_file_path example.torrent
