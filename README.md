# BitTorrent

###Dipendenze

- Installare la libreria pykka con il seguente comando:

```
pip3 install pykka

```

- Installare la libreria termicolor con il seguente comando:

```
pip3 install termicolor

``` 

### Tracker

```
cd tracker

```

- Per fare la build del progetto ed avviare il tracker

```
cd cmake-build-debug
make
./tracker

```


### Client

```
cd client

```

- Per creare un nuovo file torrent (con nome example.torrent) eseguire il comando di seguito

```
python3 torrent_file_creator.py --input_file_path example-image.jpg --torrent_file_name example.torrent --tracker_ip 127.0.0.1 --tracker_port 6881 --piece_length 256

```
- Per avviare un peer leecher (il file scaricato verrà creato nello stesso path in cui si trova il client)

```
python3 main.py --torrent_file_path example.torrent

```
- Per avviare un peer seeder (il file da caricare deve trovarsi nello stesso path in cui si trova il client)

```
python3 main.py --torrent_file_path example.torrent

```

### Test

```
cd test

```

- Avviare il tracker 

```
cd tracker/cmake-build-debug
make
./tracker

```

- Creare il file torrent (verrà contattato il tracker per creare la torrent session) ed avviare il seeder

```
cd seeder
python3 torrent_file_creator.py --input_file_path example-image.jpg --torrent_file_name example.torrent --tracker_ip 127.0.0.1 --tracker_port 6881 --piece_length 256
python3 main.py --torrent_file_path example.torrent --seeder

```

- Avviare ciascun leecher dopo aver copiato all'interno della propria directory il file torrent creato prima

```
cd leecher1 (leecher2)
python3 main.py --torrent_file_path example.torrent

```



