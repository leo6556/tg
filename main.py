from telegram import Update
from telegram import ParseMode
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import MessageHandler
from telegram.ext import ConversationHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler
import time

from pprint import pprint
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

import sqlite3 as sq
import create_database as dtb

import random
CRED_FILE = 'creds.json'
spreadsheets_id = '1DjGp4T1w_ChKieeLKbrNJVFkP6MTwlBbSHiT5u6zeik'

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CRED_FILE,
    [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

DATE, POINT, END, TIME, FINAL_CHECK, CHAT = 0,1,2,4, 5, 6


def echo(update: Update, context: CallbackContext):

    if update.effective_message.text == '/sighup':
        update.message.reply_text('Вы уже начинали выше оформлять заказ 👆🏼'
                                  ' закончите или приостановите его'
                                  )
        return


    update.message.reply_text(text='Если хотите записаться в салон красоты, нажмите на команду 👉🏼 "/start"')

def start(update: Update, context: CallbackContext):

    name = update.message.chat.full_name


    text = [
        f'*Доброго времени суток*, {name} 🤗',
        "Добро пожаловать в салон красоты *'Beauty Girls'!*  ",
        '',
        'Буквально за минуту ты можешь посмотреть цены и записаться на необходимую процедуру 🤓',
        '',

        '*Выбери нужную операцию* (можно просто нажать на //команду):',
        '',
        '🖌 /sigh_up -- записаться на прием',
        '',
        '💵 /price -- цены на наши услуги',
        '',
        "📋 /my_orders -- мои заказы",
        '',
        "🤝 /help -- помощь"

    ]

    update.message.reply_text(text='\n'.join(text),
                              parse_mode=ParseMode.MARKDOWN)


def markup_base():
    keyboard = [
        [
            InlineKeyboardButton('Стрижка 💇🏼‍♀️', callback_data='haircut'),
            InlineKeyboardButton('Окрашивание 👩🏼‍🦰', callback_data='hair')
        ],
        [
            InlineKeyboardButton('Маникюр 💅🏼', callback_data='manicure'),
            InlineKeyboardButton('Педикюр 👣', callback_data='pedicure')
        ],
        [
            InlineKeyboardButton('Уход за лицом 💆🏼‍♀️', callback_data='face')
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def markup_base2():
    keyboard = [
        [
            InlineKeyboardButton('Стрижка', callback_data='haircut2'),
            InlineKeyboardButton('Окрашивание', callback_data='hair2')
        ],
        [
            InlineKeyboardButton('Уход за лицом', callback_data='face2'),
            InlineKeyboardButton('Маникюр', callback_data='manicure2')
        ],
        # [
        #     InlineKeyboardButton('Педикюр', callback_data='pedicure2')
        # ],
        [
            InlineKeyboardButton('Приостановить заказ', callback_data='stop')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def markupDate():
    b = time.asctime()
    print(b)
    # if int(b[7:11].replace(' ', '')) < 2:
    #     c = f'0{b[9:11]}'
    # else:
    #     c = int(b[7:10])

    c = int(b[7:10])
    print(c)

    k = b[4:7]




    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheets_id,
        range='A2:A32',
        majorDimension='COLUMNS').execute()  # вместо rows можно COLUMNS
    print(values['values'][0])

    f = values['values'][0]

    # f = values['values'][0].index(str(c))
    # print(f)
    # print(c)

    month = {'Sep':'сен', 'Oct':'окт', 'Nov':'нояб', 'Dec':'дек', 'Jan':'янв', 'Feb':'фев', 'Mar':'мар','Apr':'апр', 'May':'мая', 'Jun':'июн',
             'Jul':'июл','Aug':'авг'}
    month2 = {'Sep': 'окт', 'Oct': 'нояб', 'Nov': 'дек', 'Dec': 'янв', 'Jan': 'фев', 'Feb': 'мар', 'Mar': 'апр',
             'Apr': 'мая', 'May': 'июн', 'Jun': 'июл',
             'Jul': 'авг', 'Aug': 'сен'}

    if c <= 23:
        keyboard = [
            [
                InlineKeyboardButton(f"{b} {month[k]}", callback_data=f'date{b}') for b in f[c:c + 4]
            ],
            [
                InlineKeyboardButton(f"{b} {month[k]}", callback_data=f'date{b}') for b in values['values'][0][c + 4:c + 8]
            ],
            [
                InlineKeyboardButton('Приостановить заказ', callback_data='stop')
            ],


        ]
    elif c >= 27:

        keyboard = [
            [
                InlineKeyboardButton(f"{b} {month[k]}", callback_data=f'{b}') for b in values['values'][0][c:]

            ],
            [
                InlineKeyboardButton(f"{p} {month2[k]}", callback_data=f'{b}') for p in values['values'][0][:4]
            ],
            [
                InlineKeyboardButton('Приостановить заказ', callback_data='stop')
            ],

        ]
    else:

        keyboard = [
            [
                InlineKeyboardButton(f"{b} {month[k]}", callback_data=f'{b}') for b in values['values'][0][c:c+4]

            ],
            [
                InlineKeyboardButton(f"{p} {month2[k]}", callback_data=f'{p}') for p in values['values'][0][c+6:]
            ],
            [
                InlineKeyboardButton('Приостановить заказ', callback_data='stop')
            ],
        ]


    return InlineKeyboardMarkup(keyboard)

def markup_back():
    keyboard = [
        [
            InlineKeyboardButton('Назад', callback_data='back')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def markup_YN():
     keyboard = [
         [
             InlineKeyboardButton('Все верно', callback_data='ok'),
             InlineKeyboardButton('Отменить', callback_data='revoke'),
             InlineKeyboardButton("Заново", callback_data='restart')
         ]
     ]
     return InlineKeyboardMarkup(keyboard)

def markup_YN2():

    keyboard = [
        [
            InlineKeyboardButton('Удалить', callback_data='delete'),
            InlineKeyboardButton('Вернуться', callback_data='nomore2')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def markup_orders():
    keyboard = [
        [
            InlineKeyboardButton('Подробнее', callback_data='more'),
            InlineKeyboardButton('Отменить', callback_data='stopit')
        ]

    ]
    return InlineKeyboardMarkup(keyboard)

def markup_orders2():
    keyboard = [
        [
            InlineKeyboardButton('Cкрыть', callback_data='nomore'),
            InlineKeyboardButton('Отменить', callback_data='stopit')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)



def price_list(update: Update, context: CallbackContext):
    update.message.reply_text('Что тебя интересует? 😊',
                              reply_markup=markup_base())

def callback(update:Update, context:CallbackContext):

    query = update.callback_query
    data_1 = query.data

    callback_1_list = ['haircut', 'hair', 'manicure', 'pedicure', 'back', 'face']

    while data_1 in callback_1_list:
        if data_1 == 'haircut':

            query.edit_message_text('''
                *Услуги парикмахера* 💇🏼‍♀️
💈️ Стрижка -- 2400,
💈️ Оформление челки -- 800,
💈️ Подровнять кончики -- 1200,
💈️ Модельная укладка -- 1800
        ''',
                                    reply_markup=markup_back(),
                                    parse_mode=ParseMode.MARKDOWN)
        elif data_1 == 'back':
            query.edit_message_text('Что тебя интересует? 😊',
                                    reply_markup=markup_base())
        elif data_1 == 'hair':
            query.edit_message_text('''
                *Окрашивание* 👩🏼‍🦰
💈️ Окрашивание в один тон -- 4500,
💈️ Окрашивание корней -- 3200,
💈️ Тонирование -- 2000''',
                                    reply_markup=markup_back(),
                                    parse_mode=ParseMode.MARKDOWN)
        elif data_1 == 'face':
            query.edit_message_text('''
                *Уход за лицом* 💆🏼‍♀️
💈️ Механ-ая чистка лица -- 3200,
💈️ Вак-ая чистка лица antiage -- 4200
💈️ Ультразвуковой пилинг -- 1800,
''',
                                    reply_markup=markup_back(),
                                    parse_mode=ParseMode.MARKDOWN)
        elif data_1 == 'manicure':
            query.edit_message_text('''
                *Маникюр* 💅🏼
💈 Маникюр классичкеский - 850,
💈 Маникюр аппаратный -- 1250,
💈 Покрытие - 900,
💈 Снятие - 150''',
                                    reply_markup=markup_back(),
                                    parse_mode=ParseMode.MARKDOWN)
        elif data_1 == 'pedicure':
            query.edit_message_text('''
                *Педикюр* 👣
💈 Педикюр классический -- 1600,
💈 Педикюр аппаратный -- 1800,
''',
                                    reply_markup=markup_back(),
                                    parse_mode=ParseMode.MARKDOWN)

    if data_1 == 'more':

        true_text = update.effective_message.text
        query.edit_message_text(text=f'{true_text}\n'
                                     f'📍Адрес: ул. Фадеева, 32\n'
                                     f'📍Часы работы с 10:00 до 20:00\n'
                                     f'📍Связь: (383) 263-16-19',
                                reply_markup=markup_orders2())
    elif data_1 == 'nomore':
        true_text = update.effective_message.text
        query.edit_message_text(text=true_text[:-78],
                                reply_markup=markup_orders())

    elif data_1 == 'stopit':
        true_text = update.effective_message.text
        query.edit_message_text(text=f'{true_text[:63]}\n\n*Вы уверены, что хотите удалить заказ?🤔*',
                                reply_markup=markup_YN2(),
                                parse_mode=ParseMode.MARKDOWN)
    elif data_1 == 'nomore2':
        true_text = update.effective_message.text
        query.edit_message_text(text=true_text[:56], reply_markup=markup_orders())

    elif data_1 == 'delete':

        true_text = update.effective_message.text

        #вытаскиваем дату, время   и ключевое значение

        num_ord = true_text[15:19]
        D = int(true_text[27:29])
        T = true_text[58:60]
        print(T)


        query.edit_message_text('Заказ расформирован 😌')

        with sq.connect('client_orders.db') as con:

            chat_id = update.effective_message.chat_id

            cur = con.cursor()

            cur.execute(f'DELETE FROM orders WHERE random LIKE {num_ord}')
            result = cur.fetchall()
            print(result)



        #Внести UPDATE in googlesheets

        dict_time = {'08':'B','09':'C','10':'D','11':'E','12':'F','13':'G'}


        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheets_id,
            body={
                'valueInputOption': 'USER_ENTERED',
                'data': [
                    {'range': f'{dict_time[T]}{int(D)+1}',
                     'majorDimension': 'COLUMNS',
                     'values': [['да']]},

                ]
            }
        ).execute()



def my_orders(update:Update, context:CallbackContext):

    chatid_data = update.message.chat_id

    # Подклдючение к таблице GOOGLE SHEET

    with sq.connect('client_orders.db') as con:
        cur = con.cursor()

        cur.execute(f'SELECT text FROM orders WHERE {chatid_data}=chat_id')
        result = cur.fetchall()


        # От ошибки, если заказов нет

        if len(result) > 0:
            for i in range(len(result)):
                update.message.reply_text(text=result[i][0],
                                          reply_markup=markup_orders())
        else:
            update.message.reply_text('У вас пока нет заказов.')

def help(update:Update, context:CallbackContext):
    update.message.reply_text(''' 
📍 Список команд: /sighup, /price,   
/myordedrs, /help
📍 Для того, чтобы активировать команду можно: или нажать прямо на команду (она выделеяется синим
 шрифтом) или отправить команду обычной клавиатурой.
📍 Пожелания для улучшения сервиса и отладки ошибок можете направлять на контакт: @admin_tg
''',
                             )



def start_conv(update:Update, context:CallbackContext):

    update.message.reply_text(
        text='Выберите нужную услугу 💁‍♀️',
        reply_markup=markup_base2()
    )

    return POINT

def date_han(update:Update, context:CallbackContext):

    point = update.callback_query.data
    # print(point)

    if point == 'stop':
        update.callback_query.edit_message_text('Оформление заказа приостановлено 😌')
        return ConversationHandler.END

    #Защита от спутывания callback-ов
    list_callback1 = ['haircut','hair', 'pedicure', 'manicure', 'face', 'back', 'more', 'nomore',
                      'stopit', 'nomore2', 'delete']
    while point in list_callback1:
        callback(update=update, context=context)


#Если КОНЧИЛОСЬ СВОБОДНОЕ ВРЕМЯ ВОЗВРАЩАЕТ К ВЫБОРУ ДРУГОЙ ДАТЫ
    if point == 'another':

        # chat_id = update.callback_query.message.chat_id

        update.callback_query.edit_message_text(
            text='Выберите удобныйц для вас день 📆',
            reply_markup=markupDate()
        )
        return TIME


    context.user_data[POINT] = point


    update.callback_query.edit_message_text(
        text='Выберите удобныйц для вас день 📆',
        reply_markup=markupDate()
    )
    return TIME

def time_han(update:Update, context:CallbackContext):
    callback_data = update.callback_query.data
    # print(callback_data)
    context.user_data[DATE] = callback_data

    if callback_data == 'stop':
        update.callback_query.edit_message_text('Оформление заказа приостановлено 😌')
        return ConversationHandler.END

    # Защита от спутывания callback-ов
    list_callback1 = ['haircut','hair', 'pedicure', 'manicure', 'face', 'back', 'more', 'nomore',
                      'stopit', 'nomore2', 'delete']

    while callback_data in list_callback1:
        callback(update=update, context=context)

    c = int(callback_data[-2:])
    RANGE = f'A{c+1}:G{c+1}'

    valuesYN = service.spreadsheets().values().get(
        spreadsheetId=spreadsheets_id,
        range=f'A{c+1}:G{c+1}',
        majorDimension='ROWS').execute()  # вместо rows можно COLUMNS

    newvaluesYN = valuesYN['values'][0][1:]


    valuesTIME = service.spreadsheets().values().get(
        spreadsheetId=spreadsheets_id,
        range='B1:G1',
        majorDimension='ROWS').execute()  # вместо rows можно COLUMNS

    newvaluesTIME = valuesTIME['values'][0]

    list_time = []

    while len(newvaluesYN) > 0:
        if newvaluesYN[-1:][0] == 'да':
            list_time.append(newvaluesTIME[-1])

            newvaluesTIME = newvaluesTIME[:-1]
            newvaluesYN = newvaluesYN[:-1]

            # print(list_time)
        else:
            newvaluesTIME = newvaluesTIME[:-1]
            newvaluesYN = newvaluesYN[:-1]

    list_time = list_time[::-1]

    # Если КОНЧИЛОСЬ СВОБОДНОЕ ВРЕМЯ ВОЗВРАЩАЕТ К ВЫБОРУ ДРУГОЙ ДАТЫ
    if len(list_time) == 0:

        mark = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton('Выбрать другой день', callback_data='another')
                ]
            ]
        )
        update.callback_query.edit_message_text(
            text='К сожалению свободное время кончилось',
            reply_markup=mark
        )
        return POINT


    markup = InlineKeyboardMarkup(
        inline_keyboard= [
            [
                InlineKeyboardButton(f'{i}', callback_data=f'time{i[:2]}') for i in list_time
            ],
            [
                InlineKeyboardButton('Приостановить заказ', callback_data='stop')
            ],
        ]
    )


    update.callback_query.edit_message_text('Выберите удобное  время 🕓',
                                           reply_markup=markup)

    return FINAL_CHECK

def final_check(update:Update, context:CallbackContext):

    callback_data = update.callback_query.data
    # print(callback_data)
    context.user_data[TIME] = callback_data[-2:]

    if callback_data == 'stop':
        update.callback_query.edit_message_text('Оформление заказа приостановлено 😌')
        return ConversationHandler.END

    # Защита от спутывания callback-ов
    list_callback1 = ['haircut','hair', 'pedicure', 'manicure', 'face', 'back', 'more', 'nomore',
                      'stopit', 'nomore2', 'delete']
    while callback_data in list_callback1:
        callback(update=update, context=context)

    dict_point = {'haircut2':'Стрижка', 'hair2':'Окрашивание', 'face2': 'Уход за лицом',
                  'manicure2' : 'Маникюр', 'pedicure2' : 'Педикюр'}

    rand = random.randint(1000, 9999)

    update.callback_query.edit_message_text(f'''
  *Ваш заказ* 🔖: # {rand}
*Дата* - {context.user_data[DATE][-2:]},
*Услуга* -  {dict_point[context.user_data[POINT]]},
*Время* - {context.user_data[TIME]}:00

Проверьте детали заказа 💁‍♀️
''',
                                            reply_markup=markup_YN(),
                                            parse_mode=ParseMode.MARKDOWN)
    return END

def is_end(update:Update, context:CallbackContext):


    data_2 = update.callback_query.data

    chat = update.callback_query.from_user

    # Защита от спутывания callback-ов
    list_callback1 = ['haircut','hair', 'pedicure', 'manicure', 'face', 'back', 'more', 'nomore',
                      'stopit', 'nomore2', 'delete']
    while data_2 in list_callback1:
        callback(update=update, context=context)


    if data_2 == 'ok':

        text_order = str(update.effective_message.text)
        rand = text_order[15:19]
        # print(rand)


        #  НАДО записать заказ в базу данных

        chat_id = update.callback_query.message.chat_id
        # print(chat_id)


        with sq.connect('client_orders.db') as con:
            values_text = f'{chat_id}, "{text_order[:-29]}", {rand}'
            # print(values_text)

            cur = con.cursor()

            cur.execute(f'INSERT INTO orders (chat_id, text, random) VALUES({values_text})')

        #Внести UPDATE in googlesheets

        dict_time = {'08':'B','09':'C','10':'D','11':'E','12':'F','13':'G'}

        D = context.user_data[DATE][-2:]
        # print(D)
        T = context.user_data[TIME]
        # print(T)

        values = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheets_id,
            body={
                'valueInputOption': 'USER_ENTERED',
                'data': [
                    {'range': f'{dict_time[T]}{int(D)+1}',
                     'majorDimension': 'COLUMNS',
                     'values': [['нет']]},

                ]
            }
        ).execute()


      # Отправить администратору информацию о заказе
        update.effective_message.forward(
            chat_id='1790158717',
            )


        update.callback_query.edit_message_text(text='Вы записались 🤗'
                                                     ' Cвои заказы можете посмотреть по команде /myorders',
                                                )

        return ConversationHandler.END

    elif data_2 == 'revoke':
        update.callback_query.edit_message_text('Заказ не сформирован')
        return ConversationHandler.END
    else:
        update.callback_query.edit_message_text('Давайте начнем сначала, нажмите на команду /sighup')
        return ConversationHandler.END

def cancel_han(update:Update, context:CallbackContext):
    update.message.reply_text(
        'Если хотите начать оформлять заказ нажмите на /sighup'
    )
    return ConversationHandler.END




def main():
    updater = Updater(
        token='1932460705:AAGmuy7377SjrfKuner8vFt4PLbktHktzWA')



    conv_han = ConversationHandler(
        entry_points= [
            CommandHandler('sighup', start_conv)
        ],
        states= {
            POINT: [
                CallbackQueryHandler(date_han, pass_user_data=True)
            ],
            TIME: [
                CallbackQueryHandler(time_han, pass_user_data=True)
            ],
            FINAL_CHECK: [
                CallbackQueryHandler(final_check, pass_user_data=True)
            ],
            END: [
                CallbackQueryHandler(is_end, pass_user_data=True)
            ]
        },
        fallbacks= [
            CommandHandler('stop_register', cancel_han)
        ],


    )

    updater.dispatcher.add_handler(conv_han)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('price', price_list))
    updater.dispatcher.add_handler(CommandHandler('myorders', my_orders))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    updater.dispatcher.add_handler(MessageHandler(Filters.all, echo))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback=callback))

    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()