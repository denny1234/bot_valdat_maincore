#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""


import pymysql
import logging
#bot validasi hendra
import validasi
#bot validasi TELKOM UNIVERSITY
import psb_sales
#bot fala, pkl UB
#spiegan
import omset
import expand
import migrate


import urllib.request
import requests,json
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
TOKEN = "900688850:AAE4KtOWwlNlIRnf-JgtQPxfAyRLpceApxA"
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MAINCORE_ODP,ODP_LOCATION,ODC_LOCATION,MAINCORE_ODC,CEK_MYIR= range(5)

def connection():
    conn = pymysql.connect('10.112.82.94','ikrom','akuadmindb','valdat_test')
    # conn = pymysql.connect('localhost','root','','daman')
    return conn

def ValdatMaincoreOdc(update, context):
    user = update.message.from_user
    update.message.reply_text('''
ODC-BLB-FBM KAP 144
IN
OTB 1 PORT 5 CORE 5
TO
SPL-B 5 PORT 1,2,3
TO
OTB 9 PORT 6,7,8 CORE 6,7,8
DS 3 KAP 12 CORE 6,7,8
ODP-BLB-FBM/12
KET : FEEDER LOSS
''')
    return MAINCORE_ODC

def MaincoreOdc(update, context):
    context.user_data.clear()
    user = update.message.from_user
    split_message = update.message.text.splitlines()

    if len(split_message) != 10:
        update.message.reply_text('Input anda kurang atau berlebih silahkan ulangi lagi /start')
        return ConversationHandler.END        
    #
    odc                         = split_message[0].split()
    odc_in                      = split_message[2].split()
    odc_split                   = split_message[4].split()
    odc_out                     = split_message[6].split()
    distribusi                  = split_message[7].split()
    odc_out_port,odc_out_core,odc_splt_out,d_core = {},{},{},{}

    if len(odc_split[3].split(',')) == 1 and len(odc_out[3].split(',')) == 1 and len(odc_out[5].split(',')) == 1 and  len(distribusi[5].split(',')) == 1:
        odc_out_port = odc_out[3]
        odc_out_core = odc_out[5]
        odc_splt_out = odc_split[3]
        d_core       = distribusi[5]

    elif len(odc_split[3].split(',')) >= 1 and len(odc_out[3].split(',')) >= 1 and len(odc_out[5].split(',')) >= 1 and len(distribusi[5].split(',')) >= 1:
        if len(odc_split[3].split(',')) != len(odc_out[3].split(',')) or len(odc_split[3].split(',')) != len(odc_out[5].split(',')) or len(odc_split[3].split(',')) != len(distribusi[5].split(',')):
            update.message.reply_text('Jumlah port splitter dan dengan panel out(port / core) atau port distribusi tidak sama, silahkan ulang lagi /start')
            return ConversationHandler.END
        odc_out_port = odc_out[3].split(',')
        odc_out_core = odc_out[5].split(',')
        odc_splt_out = odc_split[3].split(',')
        d_core       = distribusi[5].split(',')
    
    for x in range(len(odc_out_port)):
        detail                        = {}
        #1
        detail['odc_name']            = odc[0]
        detail['sto']                 = odc[0].split('-')[1]
        detail['odc_kap']             = odc[2]
        #3
        detail['in_tray']             = odc_in[1]
        detail['in_port']             = odc_in[3]
        detail['in_core']             = 0#odc_in[5]
        #5
        if len(odc_split[1]) > 1:
            detail['splt_name']       = odc_split[0]+'.1-'+odc_split[1]
        else:
            detail['splt_name']       = odc_split[0]+'.1-0'+odc_split[1]
        detail['splt_out']            = odc_splt_out[x]
        #7
        detail['out_tray']            = odc_out[1]
        detail['out_port']            = odc_out_port[x]
        detail['out_core']            = odc_out_core[x]
        #8
        detail['distribusi_ke']       = distribusi[1]
        detail['distribusi_kap']      = distribusi[3]
        detail['distribusi_core']     = d_core[x]
        #9
        detail['odp_name']                 = split_message[8]
        #10
        detail['description']         = split_message[9].split(':')[1]
        #10
        # detail['sto']                 = split_message[9].split()[1]
        # #11
        # detail['cap_dis']             = split_message[10].split()[1]
        # kapasitas in and out panel
        if detail['odc_kap'] == '144':
            detail['in_kap']          = 12
            detail['out_kap']         = 12
        elif detail['odc_kap'] == '288':
            detail['in_kap']          = 24
            detail['out_kap']         = 24

        
        context.user_data[x] = detail
    logger.info(context.user_data)
    update.message.reply_text('Masukkan koordinat ODC')

    return ODC_LOCATION

def odc_location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    location = {}
    location['odc_lat']             = user_location.latitude
    location['odc_long']            = user_location.longitude
    for x in range(len(context.user_data)):
        context.user_data[x].update(location)
    
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)

    data    = context.user_data 
    sql_odc     = ""
    sql_maincore = {}
    conn    = connection()
    cursor  = conn.cursor()
    cursor.execute("select id from valdat_sto where abbreviation_name = '"+str(data[0]['sto'])+"'")
    id_sto = cursor.fetchone()

    for x in range(len(data)):
        # sql_odc = "(NULL,'{}','{}','{}',{},'{}',{},'{}')".format(str(data[x]['odc_name']),str(data[x]['odc_lat']),data[x]['odc_long'],int(data[x]['odc_kap']),str(data[x]['sto']),int(data[x]['cap_dis']),str(data[x]['description']))
        sql_odc = "('{}','{}','{}',{},'{}',{})".format(str(data[x]['odc_name']),str(data[x]['odc_lat']),str(data[x]['odc_long']),int(data[x]['odc_kap']),str(data[x]['description']),int(id_sto[0]))
        sql_maincore[x] = "(NULL,{},{},{},{},'{}',{},{},{},{},{},{},{},{},{},{})".format(
            int(data[x]['in_tray']),
            int(data[x]['in_port']),
            int(data[x]['in_core']),
            int(data[x]['in_kap']),
            str(data[x]['splt_name']),
            int(data[x]['splt_out']),
            int(data[x]['out_tray']),
            int(data[x]['out_port']),
            int(data[x]['out_core']),
            int(data[x]['out_kap']),
            int(data[x]['distribusi_ke']),
            int(data[x]['distribusi_kap']),
            int(data[x]['distribusi_core']),
            "id_to_odc",
            "id_to_odp"
            )
        # update.message.reply_text(data[x])
    # sql_maincore = sql_maincore[1:]
    # update.message.reply_text(sql_maincore)
    # print("insert into valdat_odc (name,latitude,longitude,cap,description) values"+sql_odc+"")
    cursor.execute("select id from valdat_odpmaster where name = '"+str(data[0]['odp_name'])+"'")
    id_odp = cursor.fetchone()
    if id_odp is None:
        cursor.execute("insert into valdat_odpmaster (name) values ('"+str(data[0]['odp_name'])+"')")
        conn.commit()
        id_odp = cursor.lastrowid
    else:
        id_odp = int(id_odp[0])

    try:
        cursor.execute("insert into valdat_odc (name,latitude,longitude,cap,description,sto_id) values"+sql_odc+"")
        conn.commit()
    except:
        conn.rollback()
        # conn.close()
    try:
        cursor.execute("select id from valdat_odc where name = '"+str(data[0]['odc_name'])+"'")
        id_odc = int(cursor.fetchone()[0])
        for x in range(len(sql_maincore)):
            sql_maincore[x] = sql_maincore[x].replace("id_to_odc",str(id_odc))
            sql_maincore[x] = sql_maincore[x].replace("id_to_odp",str(id_odp))
            cursor.execute("select count(id) from valdat_maincore where distribution_to = "+data[x]['distribusi_ke']+" and distribution_cap = "+data[x]['distribusi_kap']+" and distribution_core = "+data[x]['distribusi_core']+" and odc_id = "+str(id_odc))
            exiss = int(cursor.fetchone()[0])
            if exiss<1:
                # update.message.reply_text(sql_maincore[x])
                cursor.execute("insert into valdat_maincore values"+sql_maincore[x]+"")
                conn.commit()
            # else:
                # update.message.reply_text("data maincore \nODC = "+data[0]['odc_name']+" \ndistribution_to = "+data[x]['distribusi_ke']+" and \ndistribution_cap = "+data[x]['distribusi_kap']+" and \ndistribution_core = "+data[x]['distribusi_core']+" sudah ada ")
        update.message.reply_text('Terima Kasih, Input Sukses')
    # conn.commit()
    except:
        update.message.reply_text("Gagal input data  odc, ulangi lagi /odc")
        conn.rollback()
        conn.close()
        return MAINCORE_ODC

    conn.close()
    # update.message.reply_text('Terima Kasih Anda telah berhasil input Validasi Maincore, klik /start untuk validasi lagi')

    
    return ConversationHandler.END

def ValdatMaincoreOdp(update, context):
    user = update.message.from_user
    update.message.reply_text('''
ODP-BLB-FBM/12 KAP 16
SPL-C,SPL-C,SPL-A
QRCODE ODP : T3P0DXI5KKFM
QRCODE PORT : T3P0MUTW56R8 , T3P0FLL5638K
ALAMAT : PERUMAHAN PLAOSAN PERMAI BLOK  D-69
KELURAHAN : PANDANWANGI
KECAMATAN : BELIMBING
ODC-BLB-FBM
KET : GENDONG
''')
    return MAINCORE_ODP


def MaincoreOdp(update, context):
    context.user_data.clear()
    user = update.message.from_user
    split_message = update.message.text.splitlines()
    if len(split_message) != 9:
        update.message.reply_text('Input anda kurang atau berlebih silahkan ulangi lagi /start')
        return ConversationHandler.END        
    # qrcode_port                 = split_message[3].split(':')
    # odp_qr= {}

    # if len(qrcode_port[1].split(',')) == 1:
    #     odp_qr                  = qrcode_port[1]
    # odp_qr                  = qrcode_port[1].split(',')
    
    # for x in range(len(odp_qr)):
    detail = {}
    detail['odp_name']            = split_message[0].split()[0]

    detail['splitter_no']         = '1'
    detail['splitter_name']       = split_message[1]
    detail['splitter_kap']        = split_message[0].split()[2]

    detail['odp_qrcode']          = split_message[2].split(':')[1]
    detail['odp_port_qrcode']     = split_message[3]
    detail['odp_address']         = split_message[4].split(':')[1]
    detail['odp_kelurahan']       = split_message[5].split(':')[1]
    detail['odp_kecamatan']       = split_message[6].split(':')[1]
    detail['odc_name']            = split_message[7]
    detail['description']         = split_message[8].split(':')[1]
    context.user_data['data'] = detail

    logger.info(context.user_data)
    update.message.reply_text('Masukkan koordinat ODP')

    return ODP_LOCATION

def odp_location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    location = {}
    location['odp_lat']             = user_location.latitude
    location['odp_long']            = user_location.longitude
    context.user_data['data'].update(location)

    data = context.user_data['data']
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    sql_distribusi,sql_odp = "",""

    conn    = connection()
    cursor  = conn.cursor()
    print("select id from valdat_odc where name = '"+str(data['odc_name'])+"'")
    try:
        cursor.execute("select id from valdat_odc where name = '"+str(data['odc_name'])+"'")
        id_odc = int(cursor.fetchone()[0])
    except:
        update.message.reply_text('ODC tidak terdaftar, ulangi lagi, /odc /odp')
        conn.rollback()
        # conn.close()
        # return ConversationHandler.END

    try:
        cursor.execute("select id from valdat_odpmaster where name = '"+str(data['odp_name'])+"'")
        odp_id=cursor.fetchone()
        if odp_id is None:
            sqllll = ("insert into valdat_odpmaster (name,splitter_no,splitter_name,splitter_kap,qrcode_odp,qrcode_port,address,urban_village,sub_district,lat,longitude,description,odc_id) values "+
            "('"+str(data['odp_name'])+"',"+data['splitter_no']+",'"+str(data['splitter_name'])+"',"+data['splitter_kap']+",'"+str(data['odp_qrcode'])+"','"+str(data['odp_port_qrcore'])+"','"+str(data['odp_address'])+"','"+str(data['odp_kelurahan'])+"','"+str(data['odp_kecamatan'])+"','"+str(data['odp_lat'])+"','"+str(data['odp_long'])+"','"+str(data['description'])+"',"+str(id_odc)+")")
            cursor.execute(sqllll)
            conn.commit()
            odp_id = cursor.lastrowid
        else:
            odp_id = int(odp_id[0])
    except:
        update.message.reply_text('Gagal input ODP ke database, /odc /odp')
        conn.rollback()
        # conn.close()
        # return ConversationHandler.END        
    update.message.reply_text('Terima Kasih anda berhasil validasi mancore odp')
    conn.close()
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the validation.", user.first_name)
    update.message.reply_text('Anda Telah Membatalkan Validasi, ulangi /start',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def get_myir(myir):
    url = 'http://api.indihome.co.id/api/track-view'
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Authorization": "Basic bXlpbmRpaG9tZTpwN2Qya0xYNGI0TkY1OFZNODR2Vw=="}
    payload = 'guid=myindihome#2017&code=&data={"trackId":"%s"}' % myir

    return requests.post(url, data=payload, headers=headers)

def StartCekMYIR(update, context):
    user = update.message.from_user
    update.message.reply_text("Masukkan Nomor MYIR :")
    return CEK_MYIR
def Cek_MYIR(update, context):
    # user = update.message.from_user
    # try:
    data_ = str(get_myir(update.message.text).text)
    json_ = json.loads(data_)
    data={}
    if json_['data'] == None:
        update.message.reply_text('MYIR tidak ditemukan, Masukkan Nomor MYIR lagi :',reply_markup=ReplyKeyboardRemove())
        return CEK_MYIR
    else :
        conn    = connection()
        cursor  = conn.cursor()
        cursor.execute("select foto_rumah_pelanggan,tag_lokasi_pelanggan from valdat_sales where track_id = '"+str(update.message.text)+"'")
        if cursor.fetchone() != None:
            foto_rumah_pelanggan,tag_lokasi_pelanggan = cursor.fetchone()
            data_json = json_['data']
            data['TRACK ID']           = data_json['track_id']
            data['K-CONTACT']          = json_['data']['detail'][0]['x3']
            data['NO SC']              = "-" if data_json['scid'] is None else data_json['scid']
            data['TANGGAL ORDER']      = "-" if data_json['orderDate'] is None else data_json['scid']
            data['STATUS MYIR']        = data_json['status_name']
            data['NAMA CUSTOMER']      = data_json['user_name']
            data['PAKET']              = data_json['name']
            data['ALAMAT INSTALASI']   = json_['data']['address']['address']
            data['STO']                = json_['data']['data1']['sto']
            update.message.reply_text(
        "TRACK ID : "+data['TRACK ID']+
        "\nK_CONTACT : "+data['K-CONTACT']+
        "\nNO_SC : "+data['NO SC']+
        "\nTANGGAL_ORDER :  "+data['TANGGAL ORDER']+
        "\nSTATUS : "+data['STATUS MYIR']+
        "\nNAMA_CUSTOMER : "+data['NAMA CUSTOMER']+
        "\nPAKET : "+data['PAKET']+
        "\nALAMAT_INSTALASI : "+data['ALAMAT INSTALASI']+
        "\nSTO : "+data['STO']
        # "\n foto_rumah_pelanggan    :  "+foto_rumah_pelanggan+
        # "\n tag_lokasi_pelanggan    :  "+tag_lokasi_pelanggan
        )
            update.message.reply_text("berikut foto rumah pelanggan")
            context.bot.send_photo(chat_id=update.message.chat_id,photo=open(str(foto_rumah_pelanggan),'rb'))
            update.message.reply_text("berikut lokasi rumah pelangan")
            loc = tag_lokasi_pelanggan.split(',')   
            urllib.request.urlopen("https://api.telegram.org/bot"+str(TOKEN)+"/sendlocation?chat_id="+str(update.message.chat_id)+"&latitude="+str(loc[0].strip())+"&longitude="+str(loc[1].strip())).read()
            return ConversationHandler.END
        else:
            update.message.reply_text("belum ada foto rumah pelanggan dan tangging lokasi pelanggan dari sales")
            return CEK_SC

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    valdat_maincore_odp = ConversationHandler(
        entry_points=[CommandHandler('odp', ValdatMaincoreOdp)],

        states={
            MAINCORE_ODP: [MessageHandler(Filters.text, MaincoreOdp)],
            ODP_LOCATION: [MessageHandler(Filters.location, odp_location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    valdat_maincore_odc = ConversationHandler(
        entry_points=[CommandHandler('odc', ValdatMaincoreOdc)],

        states={
            MAINCORE_ODC: [MessageHandler(Filters.text, MaincoreOdc)],
            ODC_LOCATION: [MessageHandler(Filters.location, odc_location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    cek_myir_handler = ConversationHandler(
        entry_points=[CommandHandler('cek_pelanggan', StartCekMYIR)],

        states={
            CEK_MYIR: [MessageHandler(Filters.text, Cek_MYIR)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(valdat_maincore_odp)
    dp.add_handler(valdat_maincore_odc)
    dp.add_handler(cek_myir_handler)

    #hendro
    dp.add_handler(validasi.main())

    #TEL UNIV
    psb,sales = psb_sales.main()
    dp.add_handler(psb)
    dp.add_handler(sales)

    #UB
    #spiegan
    omsets = omset.main()
    expands = expand.main()
    migrates = migrate.main()
    dp.add_handler(omsets)
    dp.add_handler(expands)
    dp.add_handler(migrates)
    # dp.add_handler(expand_omset_migrate.main())
    
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    # updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.start_webhook(listen="0.0.0.0",
        port=8443,
        url_path='900688850:AAE4KtOWwlNlIRnf-JgtQPxfAyRLpceApxA')
    updater.bot.set_webhook("https://pandaimandaman.localtunnel.me/900688850:AAE4KtOWwlNlIRnf-JgtQPxfAyRLpceApxA")
    updater.idle()

if __name__ == '__main__':
    main()

