import inquirer, re, time, os, json
from datetime import timedelta

import utils.common as common
from utils.common import Logger as Logger
import utils.vavoo as vavoo
import services

con = common.con0
con1 = common.con1
cache = common.cp

def mainMenu():
    c = []
    c.append((" ","0"))
    c.append(("Main Settings =>","main_settings"))
    c.append(("Vavoo Settings =>","vavoo_settings"))
    c.append(("List|Group|Stream Submenu =>","submenu_lgs"))
    c.append(("Generate M3U8 Lists","gen_list"))
    c.append(("Get epg.xml.gz", "get_epg"))
    c.append(("Stop Services", "stop_service"))
    c.append(("Restart Services", "restart_service"))
    c.append(("- Clean Database (LiveTV)","clean_tv_db"))
    c.append(("- Clean Database (Settings)","clean_db"))
    c.append(("- Clear Data Path","clear_data"))
    c.append(("<= Shutdown","shutdown"))
    q = [ inquirer.List("item", message="Main Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def lgsMenu():
    c = []
    c.append((" ","0"))
    c.append(("M3U List Menu =>","lmenu"))
    c.append(("Group Menu =>","gmenu"))
    c.append(("Stream Menu =>","smenu"))
    c.append(("<= Main Menu","back"))
    q = [ inquirer.List("item", message="List|Group|Stream Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def lMenu():
    c = []
    c.append(("<= Back","back"))
    c.append(("Add New List","add_list"))
    c.append(("Edit List","edit_list"))
    c.append(("Delete List","del_list"))
    q = [ inquirer.List("item", message="M3U8 List Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def gMenu():
    c = []
    c.append(("<= Back","back"))
    c.append(("Add New Group","add_group"))
    c.append(("Edit Group","edit_group"))
    c.append(("Delete Group","del_group"))
    q = [ inquirer.List("item", message="Group Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def sMenu():
    c = []
    c.append(("<= Back","back"))
    c.append(("Add Streams to Group","add_streams"))
    c.append(("Edit Streams in List","edit_streams"))
    q = [ inquirer.List("item", message="Stream Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def mainSettings():
    cur = con.cursor()
    c = []
    rows = []
    x = 0
    l = 0
    c.append(("<= Back","-1"))
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Main') + '"'):
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        if len(val) > l:
            l = len(val)
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Main') + '"'):
        rows.append(row)
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        t = '] '
        if not l - len(val) == 0:
            for i in range(0, l-len(val)):
                t += ' '
        c.append(('['+val+t+row['info'], str(x)))
        x += 1
    q = [ inquirer.List("item", message="Main Settings", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    if not quest["item"] == '-1':
        row = rows[int(quest["item"])]
        if row['type'] == 'text':
            q2 = [ inquirer.Text("input", message="edit: "+row["name"], default=row["value"]) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["input"], 'Main')
        if row['type'] == 'bool':
            values = json.loads(row['values'])
            for v in values:
                if not v == row['value']:
                    new = v
                    break
            common.set_setting(row["name"], new, 'Main')
        if row['type'] == 'select':
            c2 = []
            values = json.loads(row['values'])
            for v in values:
                c2.append(('['+values[v]+']', v))
            q2 = [ inquirer.List("item", message="select: "+row['name'], choices=c2, carousel=True) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["item"], 'Main')
    else: return 'back'
    return True


def vavooSettings():
    cur = con.cursor()
    c = []
    rows = []
    x = 0
    l = 0
    c.append(("<= Back","-1"))
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Vavoo') + '"'):
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        if len(val) > l:
            l = len(val)
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Vavoo') + '"'):
        rows.append(row)
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        t = '] '
        if not l - len(val) == 0:
            for i in range(0, l-len(val)):
                t += ' '
        c.append(('['+val+t+row['info'], str(x)))
        x += 1
    q = [ inquirer.List("item", message="EPG Settings", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    if not quest["item"] == '-1':
        row = rows[int(quest["item"])]
        if row['type'] == 'text':
            q2 = [ inquirer.Text("input", message="edit: "+row["name"], default=row["value"]) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["input"], 'Vavoo')
        if row['type'] == 'bool':
            values = json.loads(row['values'])
            for v in values:
                if not v == row['value']:
                    new = v
                    break
            common.set_setting(row["name"], new, 'Vavoo')
        if row['type'] == 'select':
            c2 = []
            values = json.loads(row['values'])
            for v in values:
                c2.append(('['+values[v]+']', v))
            q2 = [ inquirer.List("item", message="select: "+row['name'], choices=c2, carousel=True) ]
            quest2 = inquirer.prompt(q2)
            common.set_setting(row["name"], quest2["item"], 'Vavoo')
    else: return 'back'
    return True


def menu():
    menu = 'main'
    while True:
        if menu == 'msettings':
            quest = mainSettings()
            if not quest: Logger(3, 'Error!', 'main', 'settings')
            elif quest == 'back': menu = 'main'
        if menu == 'main':
            time.sleep(0.2)
            item = mainMenu()
            if item == 'submenu_lgs': menu = 'lgs'
            if item == 'main_settings':
                menu = 'msettings'
                quest = mainSettings()
                if not quest: Logger(3, 'Error!', 'main', 'settings')
                elif quest == 'back': menu = 'main'
            if item == 'shutdown':
                Logger(0, "Quitting Now...")
                services.handler('kill')
                con.close()
                break
            if item == 'stop_service': services.handler('service_stop')
            if item == 'restart_service': services.handler('service_restart')
            if item == 'clean_db':
                c = []
                c.append((" ","0"))
                c.append(("Yes","yes"))
                c.append(("No", "no"))
                c.append(("<= Back","back"))
                q = [ inquirer.List("item", message="Really Clean settings Database?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    clean = common.clean_tables('settings')
                    if not clean: Logger(3, 'Error!', 'db', 'clean')
                    else: Logger(0, 'Successful ...', 'db', 'clean')
            if item == 'clear_data':
                c = []
                c.append((" ","0"))
                c.append(("Yes","yes"))
                c.append(("No", "no"))
                c.append(("<= Back","back"))
                q = [ inquirer.List("item", message="Really Clear data Path?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    services.handler('kill')
                    clear = common.clear_cache()
                    break
            if item == 'gen_list': services.handler('m3u8_start')
            if item == 'get_epg': services.handler('epg_start')
            if item == 'vavoo_settings':
                menu = 'vsettings'
                quest = vavooSettings()
                if not quest: Logger(3, 'Error!', 'vavoo', 'settings')
                elif quest == 'back': menu = 'main'
            if item == 'clean_tv_db':
                c = []
                c.append((" ","0"))
                c.append(("Yes","yes"))
                c.append(("No", "no"))
                c.append(("<= Back","back"))
                q = [ inquirer.List("item", message="Really clean LiveTV Database?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    clean = common.clean_tables('live')
                    if not clean: Logger(3, 'Error!', 'db', 'clean')
                    else: Logger(0, 'Successful ...', 'db', 'clean')
        if menu == 'lgs':
            item = lgsMenu()
            if item == 'back': menu = 'main'
            if item == 'lmenu': menu = 'lmenu'
            if item == 'gmenu': menu = 'gmenu'
            if item == 'smenu': menu = 'smenu'
        if menu == 'lmenu':
            item = lMenu()
            if item == 'back': menu = 'lgs'
            if item == 'add_list':
                q = [ inquirer.Text("input", message="List Name", default='') ]
                quest = inquirer.prompt(q)
                cur = con.cursor()
                if quest["input"] == '': Logger(3, 'Error!', 'add', 'list')
                else:
                    cur.execute('INSERT INTO lists VALUES (NULL,"' + str(quest["input"]) + '","' + str('1') + '")')
                    con.commit()
                    Logger(0, 'Successful ...', 'add', 'list')
            if item == 'edit_list':
                c = []
                c.append(("<= Back","-1"))
                cur = con.cursor()
                cur.execute('SELECT * FROM lists WHERE custom="1" ORDER BY id ASC')
                rows = cur.fetchall()
                for d in rows:
                    c.append((str(d['name']),str(d['id'])))
                q = [ inquirer.List("item", message="Edit Playlist", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest['item'] == '-1':
                    cur.execute('SELECT * FROM lists WHERE id="' + quest["item"] + '"')
                    dat = cur.fetchone()
                    if dat:
                        q2 = [ inquirer.Text("input", message="edit", default=dat["name"]) ]
                        quest2 = inquirer.prompt(q2)
                        if quest2["input"] == '': Logger(3, 'Error!', 'edit', 'list')
                        else:
                            cur.execute('UPDATE lists SET name="' + quest2["input"] + '" WHERE id="' + quest["item"] + '"')
                            con.commit()
                            Logger(0, 'Successful ...', 'edit', 'list')
            if item == 'del_list':
                cur = con.cursor()
                c = []
                c.append(("<= Back","-1"))
                cur.execute('SELECT * FROM lists WHERE custom="1" ORDER BY id ASC')
                rows = cur.fetchall()
                for d in rows:
                    c.append((str(d['name']),str(d['id'])))
                q = [ inquirer.List("item", message="Delete Playlist", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest['item'] == '-1':
                    cur.execute('DELETE FROM lists WHERE id="'+ quest["item"] +'"')
                    con.commit()
                    Logger(0, 'Successful ...', 'delete', 'list')
        if menu == 'gmenu':
            item = gMenu()
            if item == 'back': menu = 'lgs'
            if item == 'add_group':
                c = []
                c.append(("<= Back","-1"))
                cur = con.cursor()
                for d in cur.execute('SELECT * FROM lists'):
                    c.append((str(d['name']),str(d['id'])))
                q = [ inquirer.List("item", message="Select Playlist", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest['item'] == '-1':
                    lid = quest['item']
                    q2 = [ inquirer.Text("input", message="Group Name", default='') ]
                    quest2 = inquirer.prompt(q2)
                    if quest2["input"] == '': Logger(3, 'Error!', 'add', 'group')
                    else:
                        cur.execute('INSERT INTO categories VALUES (NULL,"live","' + str(quest2["input"]) + '","' + str(lid) + '","1")')
                        con.commit()
                        Logger(0, 'Successful ...', 'add', 'group')
            if item == 'edit_group':
                cur = con.cursor()
                c = []
                c.append(("<= Back","-1"))
                tlid = None
                cur.execute('SELECT * FROM categories WHERE custom="1" ORDER BY lid ASC')
                rows = cur.fetchall()
                for d in rows:
                    if not d['lid'] == tlid:
                        cur.execute('SELECT * FROM lists WHERE id="' + str(d['lid']) + '"')
                        data = cur.fetchone()
                        c.append((data['name'] + ":",""))
                        tlid = d['lid']
                    c.append((str(d['category_name']),str(d['category_id'])))
                q = [ inquirer.List("item", message="Select Group", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest["item"] == '' and not quest["item"] == '-1':
                    cur.execute('SELECT * FROM categories WHERE category_id="' + quest["item"] + '"')
                    dat = cur.fetchone()
                    if dat:
                        q2 = [ inquirer.Text("input", message="edit", default=dat["category_name"]) ]
                        quest2 = inquirer.prompt(q2)
                        if quest2["input"] == '': Logger(3, 'Error!', 'edit', 'group')
                        else:
                            cur.execute('UPDATE categories SET category_name="' + quest2["input"] + '" WHERE category_id="' + quest["item"] + '"')
                            con.commit()
                            Logger(0, 'Successful ...', 'edit', 'group')
            if item == 'del_group':
                cur = con.cursor()
                c = []
                c.append(("<= Back","-1"))
                tlid = None
                cur.execute('SELECT * FROM categories WHERE custom="1" ORDER BY lid ASC')
                rows = cur.fetchall()
                for d in rows:
                    if not d['lid'] == tlid:
                        cur.execute('SELECT * FROM lists WHERE id="' + str(d['lid']) + '"')
                        data = cur.fetchone()
                        c.append((data['name'] + ":",""))
                        tlid = d['lid']
                    c.append((str(d['category_name']),str(d['category_id'])))
                q = [ inquirer.List("item", message="Select Group", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest["item"] == '' and not quest["item"] == '-1':
                    cur.execute('DELETE FROM categories WHERE category_id="'+ quest["item"] +'"')
                    con.commit()
                    Logger(0, 'Successful ...', 'delete', 'group')
        if menu == 'smenu':
            item = sMenu()
            if item == 'back': menu = 'lgs'
            if item == 'add_streams':
                cur = con.cursor()
                c = []
                c.append(("<= Back","-1"))
                tlid = None
                cur.execute('SELECT * FROM categories WHERE custom="1" ORDER BY lid ASC')
                rows = cur.fetchall()
                for d in rows:
                    if not d['lid'] == tlid:
                        cur.execute('SELECT * FROM lists WHERE id="' + str(d['lid']) + '"')
                        data = cur.fetchone()
                        c.append((data['name'] + ":",""))
                        tlid = d['lid']
                    c.append((str(d['category_name']),str(d['category_id'])))
                q = [ inquirer.List("item", message="Select Group", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest["item"] == '' and not quest["item"] == '-1':
                    c = []
                    c.append(("<= Back","-1"))
                    cur.execute('SELECT * FROM lists WHERE custom="0" ORDER BY id ASC')
                    rows = cur.fetchall()
                    for d in rows:
                        c.append((str(d['name']),str(d['name'])))
                    q = [ inquirer.List("item", message="Select Stream Country", choices=c, carousel=True) ]
                    quest2 = inquirer.prompt(q)
                    if not quest2["item"] == '' and not quest2["item"] == '-1':
                        c = []
                        d = []
                        e = []
                        cur1 = con1.cursor()
                        cur1.execute('SELECT * FROM channel WHERE country="'+ quest2["item"] +'" ORDER BY name ASC')
                        rows1 = cur1.fetchall()
                        for ch in rows1:
                            cids = json.loads(ch['cid'])
                            c.append((str(ch['name']), str(ch['id'])))
                            if int(quest['item']) in cids: d.append(str(ch['id']))
                            e.append(str(ch['id']))
                        q = [ inquirer.Checkbox("check", message="Add Streams", choices=c, default=d, carousel=True) ]
                        quest3 = inquirer.prompt(q)
                        for i in e:
                            if i in quest3["check"] and not i in d:
                                cur1.execute('SELECT * FROM channel WHERE id="'+ i +'"')
                                row = cur1.fetchone()
                                if row:
                                    cids = json.loads(row['cid'])
                                    cids.append(int(quest["item"]))
                                    cur1.execute('UPDATE channel SET cid="' + str(cids) + '" WHERE id="' + i + '"')
                            if i in d and not i in quest3["check"]:
                                cur1.execute('SELECT * FROM channel WHERE id="'+ i +'"')
                                row = cur1.fetchone()
                                if row:
                                    cids = json.loads(row['cid'])
                                    z = 0
                                    for u in range(0, len(cids)-1):
                                        if cids[u] == int(quest["item"]):
                                            break
                                        z += 1
                                    del cids[z]
                                    cur1.execute('UPDATE channel SET cid="' + str(cids) + '" WHERE id="' + i + '"')
                        con1.commit()
                        Logger(0, 'Successful ...', 'add', 'streams')
            # if item == 'edit_streams':
        if menu == 'vsettings':
            quest = vavooSettings()
            if not quest: Logger(3, 'Error!', 'vavoo', 'settings')
            elif quest == 'back': menu = 'main'

