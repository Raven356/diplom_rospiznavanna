import telebot
from operations.databaseOperations import DatabaseOperations
import constants
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import numpy

bot = telebot.TeleBot(constants.botApi)
dbOperations = DatabaseOperations()

def extract_unique_code(text):

    return text.split()[1] if len(text.split()) > 1 else None

def getUserId(unique_code): 

    userId = dbOperations.checkTelegramCode(unique_code)
    return userId

def save_chat_id(chat_id, userId):
    
    dbOperations.saveUserChatId(chat_id, userId)
    pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    unique_code = extract_unique_code(message.text)
    if unique_code:
        userId = getUserId(unique_code)
        if userId:
            save_chat_id(message.chat.id, userId)
            reply = "Successfully authorized. Now this account is synchronized with your profile"
    else:
        reply = "Please visit me via a provided URL from the website."
    bot.reply_to(message, reply)

@bot.message_handler(commands=['info'])
def sent_info(message):
    reply = "Available commamds: /getStatisticsByAccidents [location] [fromDate] [toDate], /getTimeReportStatistics [location] [fromDate] [toDate]"
    bot.reply_to(message, reply)

@bot.message_handler(commands=['getStatisticsByAccidents'])
def get_accidents_statistics(message):
    createPlot(message, dbOperations.getAccidentsForLocation, 'Amount of Accidents by Dates', 'Date', 'Number of Accidents', True)
    
@bot.message_handler(commands=['getTimeReportStatistics'])
def getTimeReports(message):
    createPlot(message, dbOperations.getIncidentTimeReactionStatistics, 'Time to report accidents by model compared to time to report accidents by call', 'Accident Number', 'Time', False)

def createPlot(message, func, title, xlabel, ylabel, changeDate):
    location = None
    fromDate = None
    toDate = None

    splits = message.text.split()
    if len(splits) > 1:
        location = splits[1]

        if len(splits) > 3:
            fromDate = splits[2]
            toDate = splits[3]
    else:
        bot.reply_to(message, "At least location should be specified")
        return

    results = func(location, fromDate, toDate)

    info = []
    counts = []
    sendByCol = []

    for row in results:
        date = row[0]
        count = row[1]
        if not changeDate:
            sendBy = row[2]
            sendByCol.append(sendBy)

        if changeDate:
            try:
                date = datetime.strptime(date.strip(), "%Y-%m-%d").date()
            except Exception as e:
                print(f"Issue with date value: {repr(date)}. Skipping this entry. Error: {e}")
                continue

        info.append(date)
        counts.append(count)

    fig, ax = plt.subplots(figsize=(10, 6))
    if not changeDate:
        # Filter info based on sendByCol values
        info_0 = [info[i] for i in range(len(info)) if sendByCol[i] == 0]
        info_1 = [info[i] for i in range(len(info)) if sendByCol[i] == 1]

        # Create y-values with the same length as the filtered info lists
        y_values_0 = [counts[i] for i in range(len(info)) if sendByCol[i] == 0]
        y_values_1 = [counts[i] for i in range(len(info)) if sendByCol[i] == 1]

        # Plot info_0 and info_1 with their respective y-values
        ax.plot(info_0, y_values_0, marker='o', label='send by mail', color='blue')
        ax.plot(info_1, y_values_1, marker='o', label='send by telegram', color='red')
        
        # Plot a horizontal line with y-value set to 10 for all info points
        y_values_constant = numpy.full(len(info), 10)
        ax.plot(info, y_values_constant, marker='o')
        y_values = numpy.full_like(info, 10)
        ax.plot(info, y_values, marker='o')
    else:
        ax.plot(info, counts, marker='o')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    ax.legend()
    ax.grid(True)

    canvas = FigureCanvas(fig)

    img_buf = io.BytesIO()
    canvas.print_png(img_buf)
    img_buf.seek(0)

    bot.send_photo(message.chat.id, img_buf, caption='Accident Statistics')

    plt.close(fig) 

if __name__ == '__main__':
    bot.polling()