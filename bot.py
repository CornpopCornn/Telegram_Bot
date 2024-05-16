import os
import logging
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# States for conversation handler
VERIFY, ORDER_DETAILS, DELIVERY_INFO = range(3)

# Start command
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Welcome! To place an order, we need to verify your identity. "
        "Please send a selfie and a photo of your ID, both holding a note with today's date."
    )
    return VERIFY

# Verification handler
def verify(update: Update, context: CallbackContext) -> int:
    if update.message.photo:
        user_data = context.user_data
        user_data['verification'] = user_data.get('verification', 0) + 1
        if user_data['verification'] == 2:
            update.message.reply_text("Thank you for the verification. Please enter your order details.")
            return ORDER_DETAILS
        else:
            update.message.reply_text("Great! Now send the second required photo.")
    else:
        update.message.reply_text("Please send a photo.")
    return VERIFY

# Order details handler
def order_details(update: Update, context: CallbackContext) -> int:
    context.user_data['order'] = update.message.text
    update.message.reply_text(
        "Please choose the delivery method:",
        reply_markup=ReplyKeyboardMarkup([['Delivery', 'Pickup']], one_time_keyboard=True)
    )
    return DELIVERY_INFO

# Delivery info handler
def delivery_info(update: Update, context: CallbackContext) -> int:
    delivery_method = update.message.text
    if delivery_method == 'Delivery':
        update.message.reply_text("Please enter your delivery address.")
    else:
        update.message.reply_text("You chose pickup. Please enter your preferred pickup time.")
    return ConversationHandler.END

# Cancel command
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Order cancelled.")
    return ConversationHandler.END

# Main function to start the bot
def main():
    # Set up the Updater
    updater = Updater("7096259144:AAExLF56_B0ExM8O_Str877vXNLXQkNZD2g")
    dispatcher = updater.dispatcher

    # Set up conversation handler with the states VERIFY, ORDER_DETAILS, DELIVERY_INFO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            VERIFY: [MessageHandler(Filters.photo, verify)],
            ORDER_DETAILS: [MessageHandler(Filters.text & ~Filters.command, order_details)],
            DELIVERY_INFO: [MessageHandler(Filters.text & ~Filters.command, delivery_info)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add the conversation handler to the dispatcher
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
