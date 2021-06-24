import json
import sqlite3
import olefile
import pandas as pd
import datetime
import argparse
import sys
import os
import struct
def snt(file):
    # https://www.tutorialspoint.com/python_digital_forensics/python_digital_forensics_important_artifacts_in_windows
    if not olefile.isOleFile(file):
        return "Invalid OLE file"

    ole = olefile.OleFileIO(file)
    note = {}
    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    for stream in ole.listdir():
        if stream[0].count("-") == 3:
            if stream[0] not in note:
                    note[stream[0]] = {"created": str(ole.getctime(stream[0])), "modified": str(ole.getmtime(stream[0]))}
                    content = None
            if stream[1] == '3':
                    content = ole.openstream(stream).read().decode("utf-16").rstrip("\u0000")
            if content:
                    note[stream[0]][stream[1]] = content

    db_df =  pd.read_json(json.dumps(note, indent=4, sort_keys=True))
    data_df= []
    column_df = []

    column_df = list(db_df.index.values)
    column_df[0] = 'text'
    column_df.insert(0,'id')
    temp_list = db_df.columns
    for i in range(len(list(db_df.columns.values))):
           data_df.append([temp_list[i],db_df.iloc[0,i],db_df.iloc[1,i],db_df.iloc[2,i]])
    final_df = pd.DataFrame(data = data_df , columns = column_df)
    print("StickyParser: Saving the csv file")
   
    final_df.to_csv(args.d+ 'stickynoteresultsnt-'+ now + '.csv', index=False)
    print("StickyParser: File saved.")


def plum(db):
   
    conn = sqlite3.connect(db, isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM Note", conn)
   
    if db_df['LastServerVersion'][0] is None:
        db_df = pd.read_sql_query("SELECT * FROM Note", conn)
        now = datetime.datetime.now().strftime("%Y%m%d%H%M")
        print("StickyParser: Saving the csv file")
       
        db_df.to_csv(args.d+ 'stickynoteresultplum-'+ now + '.csv', index=False)    
        print("StickyParser: File saved.")
       
    if db_df['LastServerVersion'][0] is not None:
        a = db_df.LastServerVersion.apply(json.loads).values.tolist()
        temp_df = pd.DataFrame.from_records(a)
        text_df = []
        for  no in temp_df["document"]:
            text = ""
            for block in no["blocks"]:

                for content in block["content"]:
                    text = text + content["text"] + "\r"

            text_df.append(text)
        temp_df.insert(3,"text",text_df,True)
        now = datetime.datetime.now().strftime("%Y%m%d%H%M")
        print("StickyParser: Saving the csv file")
        temp_df.to_csv(args.d+ 'stickynoteresultplum-'+ now + '.csv', index=False)    
        print("StickyParser: File saved.")
   
   

def all_same(items):
    return all(x == items[0] for x in items)

def hexdump(src, length=16):
    if all_same(src):
        strzero = "0000   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................\n"
        strzero += "..."
        return strzero
    result = []
    digits = 4 if isinstance(src, bytes) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = ' '.join(["%0*X" % (digits, x)for x in s])
        hexa = bytes(hexa, 'UTF-8')
        text = b''
        for x in s:
               #x = str(x
               if(x < 0x20 or x == 0x7F or 0x81 <= x < 0xA0):
               
                   text += b'.'
               else:
                   text += x.to_bytes(1,'big')
        result.append( b"%04X   %-*s   |%s|" % (i, length*(digits + 1),hexa, text) )

    return b'\n'.join(result)


def asciidump(src, length=80):
    if all_same(src):
      strzero = "................................................................................"
      return strzero
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
       s = src[i:i+length]
       #print(type(s))
       #s = bytes(s, 'utf-8')
       text = ''
       text = text.encode()
       for x in s:
         #x = str(x)
         if(x < 0x20 or x == 0x7F or 0x81 <= x < 0xA0):
           text += b'.'
         else:
           text += x.to_bytes(1,'big')
       result.append( b"%s" % (text) )
       
       #result = result.decode('utf-8','ignore')
       x = b'\n'.join(result)
       x.decode('utf-8',errors='ignore')
       
    return b'\n'.join(result)



def formatlist(list):
 i=0
 for el in list:
    i+=1
    if i == 10:
       if verbose == 1: print
       i=0
    else:
       if verbose == 1: print ('%5d' % el,)
 if verbose == 1: print
 
def locatetrunk ( offset ):
 nextrunk =  struct.unpack(">i", s[offset:offset+4])[0]
 if nextrunk != 0:
   return nextrunk
 else:
   return 0

def locatefreeleafs ( offset ):
  numleafpag = struct.unpack(">i", s[offset+4:offset+8])[0]
  # -24 -> bug in sqlite avoids writing in last 6 entries
  freepage = s[offset+8:offset+pagesize-24]  
  fmt = ">" + "i" * int((len(freepage)/4))
  # return only numleafpag
  return struct.unpack(fmt, freepage)[0:numleafpag]


def freepages( ):
  offset = (pagenum - 1)*pagesize
  freeleaftpages=locatefreeleafs( offset )
  nextrunk = 1
  freetrunk.append(pagenum)
  while ( nextrunk != 0 ):
    nextrunk = locatetrunk( offset )
    if nextrunk != 0:
        freetrunk.append(nextrunk)
        offset = (nextrunk - 1)*pagesize
        freeleaftpages += locatefreeleafs( offset )
   
  freeleaf = list(set(freeleaftpages))

  return freeleaf, freetrunk

def locatebtree( ):
  offset = 100
  page = 1
  while ( offset < filesize ):
      byte = s[offset]
      if byte == 13 and page not in freeleaf:
          leafpages.append(page)
      elif byte == 2 and page not in freeleaf:
          interindex.append(page)
      elif byte == 5 and page not in freeleaf:
          intertable.append(page)
      elif byte == 10 and page not in freeleaf:
          leafindex.append(page)
      if offset == 100:
          offset = 0
      offset += pagesize
      page += 1

def pagedump(pages):
 for page in pages:
    offset = (page-1  )*pagesize
    end = 0
    if page == 0 or offset == 0:
       offset += 100
       end = 100
    if page not in freeleaf and page not in freetrunk:
        numcells = struct.unpack(">H", s[offset+3:offset+5])[0]
        offcells = struct.unpack(">H", s[offset+5:offset+7])[0]
        osfree = struct.unpack(">H", s[offset+1:offset+3])[0]
        fragmented = struct.unpack(">b", s[offset+7].to_bytes(1, 'big'))[0]
        nextfb = osfree
        fbsize = 0
        if offcells == 0:
            offcells = 65536
        head = 8
        if s[offset] == 2 or 5: head = 12
        unstart = offset + head + ( numcells * 2 )
        unend = offset + offcells  - end
        freestr = s[unstart:unend]
        if ftype != "n":
            print('%-25s page: %s offset: %10s-%-10s\n' % ('Unallocated space: ', page, unstart, unend), file = file)
        if ftype == "a":
            print(asciidump(freestr),file=file)
        elif ftype == "h":
            print (hexdump(freestr),file=file)

        while ( nextfb != 0 ):
            fbsize = struct.unpack(">H", s[offset+nextfb+2:offset+nextfb+4])[0]
            fbstart = offset + nextfb + 4
            fbend = offset + nextfb + fbsize
            fbstr = s[fbstart:fbend]
            if ftype != "n":
                print ('%-25s page: %s offset: %10s-%-10s\n' % ('Freeblock space: ', page, fbstart,fbend),file=file)
            if ftype == "a":
                print (asciidump(fbstr), file=file)
            elif ftype == "h":
                print(hexdump(fbstr),file=file)
            nextfb = struct.unpack(">H", s[offset+nextfb:offset+nextfb+2])[0]
           
    elif page in freeleaf:
        freestr = s[offset:offset+pagesize]  
        if ftype != "n":
            print ('%-25s page: %s offset: %10s\n' % ('Freelist leaf page: ',page, offset),file=file)
        if ftype == "a":
            print(asciidump(freestr), file = file)

        elif ftype == "h":
            print(hexdump(freestr), file = file)

    elif page in freetrunk:
        ftstart = offset+8+(4*len(freeleaf))
        ftend = offset+pagesize
        freestr = s[ftstart:ftend]
        if ftype != "n":
            print ('%-25s page: %s offset: %10s-%-10s\n' % ('Freelist trunk space: ', page, ftstart,ftend), file = file)
        if ftype == "a":
            print (f'asciidump(freestr)', file = file)
        elif ftype == "h":
            print(hexdump(freestr), file = file)



       
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""StickyParser: Parses sticky note files in legacy snt formats or latest sqlite formats.It can also be used to recover deleted content inside sqlite. 
                                                For latest version of StickyNote, please copy everything under the %LOCALAPPDATA%\\Packages\\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbw\\LocalStatealState Folder. Run StickyPraser against the copied folder. Make sure the other files apart from the plum.sqlite are all in the same folder.
                                                 Once run, WAL/SHM files will be merged into .sqlite file.""")
    parser.add_argument('-s', nargs='?',metavar="snt file", help='Sticky note .snt file. Example: StickyParser.exe -s C:\\Users\\User\\AppData\\Roaming\\Sticky Notes\\StickyNotes.snt. Choose either -s or -p only. ', type=argparse.FileType('r'))
    parser.add_argument('-p', nargs='?',metavar="sqlite file", help='Sticky note plum.sqlite file. Example: StickyParse -s  <Path>\\plum.sqlite. Choose either -s or -p', type=argparse.FileType('r'))
    parser.add_argument('-d' ,nargs='?',metavar="File Directory", help='Specify the directory where the output should write to. Example: StickyParser -p <path> -d C:\\Users\\User\\Desktop\\')
    parser.add_argument('-r', nargs='?',metavar="sqlite file", help = 'To recover deleted content from sqlite.') 
    args = parser.parse_args()
    line = "*" * 10
    if args.d is not None:
        if args.d[-1] != '\\':
            args.d = args.d + '\\'
           
    if args.s is not None:

        print('StickyPraser: Parsing the SNT File...')
        snt(args.s.name)

    if args.p is not None:

        print('StickyPraser: Parsing the sqlite file ....')
        plum(args.p.name)
        
    if args.r is not None:
        print('StickyPraser: Attempt to recover deleted content.')
        now = datetime.datetime.now().strftime("%Y%m%d%H%M") 

        file = open(args.r + 'stickynotemetadata-' + now + '.txt','w')
        ftype = "a"
        pages = "all"
        filesize = os.path.getsize(args.r)
        freeleaf = [ ]
        freetrunk = [ ]
        btreepages = [ ]
        leafpages = [ ]
        interindex = [ ]
        intertable = [ ]
        leafindex = [ ]

        verbose = 0
        with open(args.r, 'rb') as f:
            s = f.read()


    # The header string: "SQLite format 3\000"
        hs=s[:16].rstrip(b' \t\r\n\0')
        if hs == b'SQLite format 3':
             r = " (correct)"
        else:
             r = " (incorrect)"
        file.write ('%-45s %-20s\n' % ("Header String:", str(hs) + r))

# The database page size in bytes. Must be a power of two between 512
# and 32768 inclusive, or the value 1 representing a page size of 65536
        pagesize = struct.unpack(">H", s[16:18])[0]
        if pagesize == 1:
             pagesize == 65536
        file.write ('%-45s %-20s\n'  % ("Page Size bytes:", pagesize))

# File format write version. 1 for legacy; 2 for WAL
        wver = ord(s[18:19])
        if wver == 2:
              wrel = str(wver) + " - WAL: yes"
        else:
              wrel = str(wver) + " - WAL: no"
        file.write ('%-45s %-20s\n' % ("File format write version:", wrel))

# File format read version. 1 for legacy; 2 for WAL.
        rver = ord(s[19:20])
        if rver == 2:
              rrel = str(rver) + " - WAL: yes"
        else:
              rrel = str(rver) + " - WAL: no"
        file.write ('%-45s %-20s\n' % ("File format read version:", rrel))

# Bytes of unused "reserved" space at the end of each page. Usually 0.

        if verbose == 1: f.write ('%-45s %-20s\n' % ('Bytes of unused reserved space:', s[20]))

# Maximum embedded payload fraction. Must be 64.
        if s[21] == 64:
             r = " (correct)"
        else:
             r = " (incorrect)"
        if verbose == 1: f.write ('%-45s %-20s\n' % ('Maximum embedded payload fraction:', str(s[21]) + r))

# Minimum embedded payload fraction. Must be 32.
        if s[22] == 32:
             r = " (correct)"
        else:
             r = " (incorrect)"
        if verbose == 1: f.write ('%-45s %-20s\n' % ('Minimum embedded payload fraction:', str(s[22]) + r))

# Leaf payload fraction. Must be 32.
        if s[23] == 32:
             r = " (correct)"
        else:
             r = " (incorrect)"
        if verbose == 1: f.write ('%-45s %-20s\n' % ('Leaf payload fraction:', str(s[23]) + r))

# File change counter.
        count = struct.unpack(">i", s[24:28])[0]
        file.write ('%-45s %-20s\n' % ('File change counter:', count))

# Size of the database file in pages. The "in-header database size".
        sizepag = struct.unpack(">i", s[28:32])[0]
        file.write ('%-45s %-20s\n' % ('Size of the database file in pages:', sizepag))

# Page number of the first freelist trunk page.
        pagenum = struct.unpack(">i", s[32:36])[0]
        file.write ('%-45s %-20s\n' % ('Page number of the first freelist trunk page:', pagenum))

# Total number of freelist pages.
        freenum = struct.unpack(">i", s[36:40])[0]
        file.write ('%-45s %-20s\n' % ('Total number of freelist pages:', freenum))

# The schema cookie.
        schema = struct.unpack(">i", s[40:44])[0]
        if verbose == 1: file.write ('%-45s %-20s\n' % ('The schema cookie:', schema))

# The schema format number. Supported schema formats are 1, 2, 3, and 4.
        schemav = struct.unpack(">i", s[44:48])[0]
        if schemav == 1:
             schemavs = " -  back to ver 3.0.0"
        elif schemav == 2:
             schemavs = " - >= 3.1.3 on 2005-02-19"
        elif schemav == 3:
             schemavs = " - >= 3.1.4 on 2005-03-11"
        elif schemav == 4:
             schemavs = " - >= 3.3.0 on 2006-01-10"
        else:
             schemavs = " - schema version error"
        if verbose == 1: file.write ('%-45s %-20s\n' % ('The schema format number', str(schemav) + schemavs))

# Default page cache size.
        pcachesize = struct.unpack(">i", s[44:48])[0]
        if verbose == 1: file.write ('%-45s %-20s\n' % ('Default page cache size:', pcachesize))

# The page number of the largest root b-tree page when in auto-vacuum or incremental-vacuum modes, or zero otherwise.
        vacuum = struct.unpack(">i", s[52:56])[0]
        if vacuum == 0:
             vacuums = " - not supported"
        else:
             vacuums = " "
        if verbose == 1: file.write ('%-45s %-20s\n' % ('Auto/incremental-vacuum page number:', str(vacuum) + vacuums))

# The database text encoding. A value of 1 means UTF-8. A value of 2 means UTF-16le. A value of 3 means UTF-16be.
        encod = struct.unpack(">i", s[56:60])[0]
        if encod == 1:
            encods = " - UTF-8"
        elif encod == 2:
            encods = " - UTF-16le"
        elif encod == 3:
            encods = " - UTF-16be"
        else:
             encods = " - error"
        file.write ('%-45s %-20s\n' % ('The database text encoding:', str(encod) + encods))

# The "user version" as read and set by the user_version pragma.
        userv = struct.unpack(">i", s[60:64])[0]
        if verbose == 1: file.write ('%-45s %-20s\n' % ('User version number:', userv))

# True (non-zero) for incremental-vacuum mode. False (zero) otherwise.
        incvacuum = struct.unpack(">i", s[64:68])[0]
        if incvacuum == 0:
              sinc = " - false"
        else:
              sinc = " - true"
        file.write('%-45s %-20s\n' % ('Incremental-vacuum mode:', str(incvacuum) + sinc))

        reserv = struct.unpack(">iiiiii", s[68:92])[0]
        if reserv == 0:
              strreserv = "0 (correct)"
        else:
              strreserv = "!= 0 (incorrect)"
        if verbose == 1: file.write ('%-45s %-20s\n' % ('Reserved for expansion:', strreserv))

# The version-valid-for number.
# The 4-byte big-endian integer at offset 92 is the value of the change counter
# when the version number was stored. The integer at offset 92 indicates which
# transaction the version number is valid for and is sometimes called the
# "version-valid-for number".
        verval =  struct.unpack(">i", s[92:96])[0]
        if verbose == 1: file.write ('%-45s %-20s\n' % ('The version-valid-for number:', verval))

# SQLITE_VERSION_NUMBER:
# #define SQLITE_VERSION        "3.7.13"
# #define SQLITE_VERSION_NUMBER 3007013
        vervalid = struct.unpack(">i", s[96:100])[0]
        may = vervalid / 1000000
        min = (vervalid - (may * 1000000)) / 1000
        rls =  vervalid - (may * 1000000) - (min * 1000)
        verstr = str(vervalid) + " - " + str(may) + "." + str(min) + "." + str(rls)
        file.write ('%-45s %-20s\n' % ('SQLITE_VERSION_NUMBER:', verstr))
# Freepages
    #freeleaf = [ ]
    #freetrunk = [ ]

        if freenum > 0: freeleaf,  freetrunk = freepages( )
        if verbose == 1 and freenum >0:
              file.write ("Freelist leaf pages:")
        formatlist(freeleaf)
        file.write('%-45s %-20s\n' % ('Number of freelist leaf pages:', len(sorted(set(freeleaf)))))
        locatebtree()
       
        if verbose == 1 and len(freetrunk) >0:
          file.write ("Freelist trunk pages:")
          formatlist(freetrunk)
        file.write('%-45s %-20s\n' % ('Number of freelist trunk pages:', len(freetrunk)))

        if verbose == 1 and len(leafpages) > 0:
          file.write("B-Tree leaf pages:")
          formatlist(leafpages)
        file.write ('%-45s %-20s\n' % ('Number of b-tree leaf pages:', len(leafpages)))
        if verbose == 1 and len(leafindex) >0:
          file.write ("B-Tree leaf index pages:")
          formatlist(leafindex)
        file.write ('%-45s %-20s\n' % ('Number of b-tree leaf index pages:', len(leafindex)))
        if verbose == 1 and len(interindex) >0:
          file.write ("B-Tree interior index pages:")
          formatlist(interindex)
        file.write ('%-45s %-20s\n' % ('Number of b-tree interior index pages:', len(interindex)))
        if verbose == 1 and len(intertable) >0:
          file.write ("B-Tree interior table pages:")
          formatlist(intertable)
        file.write ('%-45s %-20s\n' % ('Number of b-tree interior table pages:', len(intertable)))


        btreepages = sorted(leafpages + leafindex + interindex + intertable)
        allpag = sorted(btreepages + freeleaf + freetrunk)

        pagedump(allpag)


        if verbose == 1:
          file.write ('%-45s %-20s\n' % ('Number of detected pages:', len(allpag)))
          file.write ('%-45s %-20s\n' % ('Missing:', sizepag - len(allpag)))
        print('StickyParser: Recovered content saved on specific directory')
       


           
       
    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)



