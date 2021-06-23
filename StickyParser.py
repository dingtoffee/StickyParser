import json
import sqlite3
import olefile
import pandas as pd
import datetime
import argparse
import sys

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
    print(args.d)
    final_df.to_csv(args.d+ 'stickynoteresultsnt-'+ now + '.csv', index=False)
    print("StickyParser: File saved.")


def plum(db):

    conn = sqlite3.connect(db, isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM Note", conn)
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""StickyParser: Parses sticky note files in legacy snt formats or latest sqlite formats. 
                                                For latest version of StickyNote, please copy everything under the %LOCALAPPDATA%\\Packages\\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbw\\LocalStatealState Folder. Run StickyPraser against the copied folder. Make sure the other files apart from the plum.sqlite are all in the same folder. 
                                                 Once run, WAL/SHM files will be merged into .sqlite file.""")
    parser.add_argument('-s', nargs='?',metavar="snt file", help='Sticky note .snt file. Example: StickyParser.exe -s C:\\Users\\User\\AppData\\Roaming\\Sticky Notes\\StickyNotes.snt. Choose either -s or -p only. ', type=argparse.FileType('r'))
    parser.add_argument('-p', nargs='?',metavar="sqlite file", help='Sticky note plum.sqlite file. Example: StickyParse -s  <Path>\\plum.sqlite. Choose either -s or -p', type=argparse.FileType('r'))
    parser.add_argument('-d' ,nargs='?',metavar="File Directory", help='Specify the directory where the output should write to. Example: StickyParser -p <path> -d C:\\Users\\User\\Desktop\\')
    args = parser.parse_args()

    line = "*" * 10
    if args.d is not None:
        if args.d[-1] != '\\':
            args.d = args.d + '\\'
            
    if args.s is not None:

        print('StickyPraser: Prasing the SNT File...')
        snt(args.s.name)

    if args.p is not None:

        print('StickyPraser: Prasing the sqlite file ....') 
        plum(args.p.name)


    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)
