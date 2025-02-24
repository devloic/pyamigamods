from uade2 import Uade

uade = Uade()

#result=uade.scan_song_file('/home/lolo/mnt/WDBLACK/amiga/mods/acoustic dreams.mod')
#result=uade.scan_song_file('/home/lolo/mnt/WDBLACK/amiga/mods/awesome.cus')
result=uade.scan_song_file('/home/lolo/mnt/WDBLACK/amiga/mods/CUST.Paranoimia-1.cust')
#result=uade.scan_song_file('/home/lolo/mnt/WDBLACK/amiga/mods/futurecomposer/audacious-uade/testdata/burgertime mix.xm')



for att in [a for a in dir(result) if not a.startswith('__')]:
    x = getattr(result, att)
    print (att+":"+str(x))
    if (att=="subsong_data"):
        for att2 in [a for a in dir(x) if not a.startswith('__')]:
            y = getattr(x, att2)
            print("    "+att + ":" + str(y))
            for att3 in [a for a in dir(y) if not a.startswith('__')]:
                print("    "+"    "+att3 + ":" + str(y))