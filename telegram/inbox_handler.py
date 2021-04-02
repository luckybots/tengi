from telebot import types


class TelegramInboxHandler:
    """
    Methods of this class should be exactly the same as different options of telebot.types.Update
        see https://core.telegram.org/bots/api#update
    Don't add any other functions. In case you need some middleware logic -- create a subclass of this one.
    If  my_chat_member, chat_member will be needed - they are likely sent as Message, see telebot.types.Message.de_json
    """

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def message(self, message: types.Message) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def edited_message(self, message: types.Message) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def channel_post(self, channel_post: types.Message) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def edited_channel_post(self, edited_channel_post: types.Message) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def inline_query(self, inline_query: types.InlineQuery) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def chosen_inline_result(self, chosen_inline_result: types.ChosenInlineResult) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def callback_query(self, callback_query: types.CallbackQuery) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def shipping_query(self, shipping_query: types.ShippingQuery) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def pre_checkout_query(self, pre_checkout_query: types.PreCheckoutQuery) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def poll(self, poll: types.Poll) -> bool:
        return False

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def poll_answer(self, poll_answer: types.PollAnswer) -> bool:
        return False
