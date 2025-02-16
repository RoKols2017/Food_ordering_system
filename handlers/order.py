import logging
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Order, OrderItem, Dish
from handlers import order_utils  # новый модуль для общих функций работы с заказом

db = None

def set_db(db_instance):
    global db
    db = db_instance

# Функция для создания корзины (заказ со статусом 'cart')
def create_cart(user_id, restaurant_id):
    session = db.Session()
    try:
        from database.models import Order
        new_order = Order(
            user_id=user_id,
            restaurant_id=restaurant_id,
            status='cart',
            total_cost=0.0
        )
        session.add(new_order)
        session.commit()
        return new_order
    except Exception as e:
        session.rollback()
        logging.error("Ошибка создания корзины для пользователя %s: %s", user_id, e)
        return None
    finally:
        session.close()

def add_dish_to_cart(user_id, dish_id, quantity=1):
    dish = db.get_dish(dish_id)
    if not dish:
        return False, "Блюдо не найдено."

    # Получаем корзину (объект отсоединён)
    from handlers import order_utils
    cart = order_utils.get_current_cart(db, user_id)

    session = db.Session()
    try:
        if cart:
            cart = session.query(Order).filter_by(id=cart.id).first()
        else:
            cart = create_cart(user_id, dish.restaurant_id)
            cart = session.query(Order).filter_by(id=cart.id).first()

        if cart.restaurant_id != dish.restaurant_id:
            return False, "Нельзя добавить блюда из другого ресторана. Завершите текущий заказ."

        from database.models import OrderItem
        order_item = session.query(OrderItem).filter_by(order_id=cart.id, dish_id=dish_id).first()
        if order_item:
            order_item.quantity += quantity
            order_item.total = order_item.quantity * dish.price
        else:
            order_item = OrderItem(
                order_id=cart.id,
                dish_id=dish_id,
                quantity=quantity,
                price=dish.price,
                total=dish.price * quantity
            )
            session.add(order_item)

        # Пересчитываем общую стоимость заказа
        order_items = session.query(OrderItem).filter_by(order_id=cart.id).all()
        cart.total_cost = sum(item.total for item in order_items)
        session.commit()
        return True, "Блюдо успешно добавлено в корзину."
    except Exception as e:
        session.rollback()
        logging.error("Ошибка при добавлении блюда в корзину: %s", e)
        return False, "Ошибка при добавлении блюда в корзину."
    finally:
        session.close()

def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("order_add_"))
    def order_add_callback(call):
        try:
            parts = call.data.split("_")
            if len(parts) < 3:
                bot.answer_callback_query(call.id, "Неверные данные для добавления блюда.")
                return
            dish_id = int(parts[2])
            quantity = 1
            if len(parts) >= 4 and parts[3].isdigit():
                quantity = int(parts[3])
            success, response = add_dish_to_cart(call.from_user.id, dish_id, quantity)
            bot.answer_callback_query(call.id, response)
            # Используем функцию из order_utils для получения деталей корзины
            cart_message = order_utils.get_cart_details(db, call.from_user.id)
            bot.send_message(call.message.chat.id, cart_message)
        except Exception as e:
            logging.error("Ошибка в order_add_callback: %s", e)
            bot.answer_callback_query(call.id, "Произошла ошибка при добавлении блюда.")

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
    def back_to_main_menu_callback(call):
        from handlers import main_menu
        main_menu.send_main_menu(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("increase_"))
    def increase_quantity(call):
        try:
            item_id = int(call.data.split("_")[1])
            session = db.Session()
            from database.models import OrderItem, Dish, Order
            item = session.query(OrderItem).filter_by(id=item_id).first()
            if not item:
                bot.answer_callback_query(call.id, "Элемент не найден.")
                return
            item.quantity += 1
            dish = db.get_dish(item.dish_id)
            item.total = item.quantity * dish.price
            # Пересчёт общей стоимости корзины
            cart = session.query(Order).filter_by(id=item.order_id).first()
            order_items = session.query(OrderItem).filter_by(order_id=cart.id).all()
            cart.total_cost = sum(i.total for i in order_items)
            session.commit()
            bot.answer_callback_query(call.id, "Количество увеличено.")
            text, markup = order_utils.get_cart_details_markup(db, call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=text,
                                  reply_markup=markup)
        except Exception as e:
            session.rollback()
            bot.answer_callback_query(call.id, "Ошибка при обновлении количества.")
        finally:
            session.close()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("decrease_"))
    def decrease_quantity(call):
        try:
            item_id = int(call.data.split("_")[1])
            session = db.Session()
            from database.models import OrderItem, Dish, Order
            item = session.query(OrderItem).filter_by(id=item_id).first()
            if not item:
                bot.answer_callback_query(call.id, "Элемент не найден.")
                return
            if item.quantity > 1:
                item.quantity -= 1
                dish = db.get_dish(item.dish_id)
                item.total = item.quantity * dish.price
            else:
                # Если количество равно 1, удаляем позицию
                session.delete(item)
            # Пересчёт общей стоимости корзины
            cart = session.query(Order).filter_by(id=item.order_id).first()
            order_items = session.query(OrderItem).filter_by(order_id=cart.id).all()
            cart.total_cost = sum(i.total for i in order_items)
            session.commit()
            bot.answer_callback_query(call.id, "Количество уменьшено.")
            text, markup = order_utils.get_cart_details_markup(db, call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=text,
                                  reply_markup=markup)
        except Exception as e:
            session.rollback()
            bot.answer_callback_query(call.id, "Ошибка при обновлении количества.")
        finally:
            session.close()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("remove_"))
    def remove_item(call):
        try:
            item_id = int(call.data.split("_")[1])
            session = db.Session()
            from database.models import OrderItem, Order
            item = session.query(OrderItem).filter_by(id=item_id).first()
            if not item:
                bot.answer_callback_query(call.id, "Элемент не найден.")
                return
            order_id = item.order_id
            session.delete(item)
            # Пересчёт общей стоимости корзины
            cart = session.query(Order).filter_by(id=order_id).first()
            order_items = session.query(OrderItem).filter_by(order_id=order_id).all()
            cart.total_cost = sum(i.total for i in order_items)
            session.commit()
            bot.answer_callback_query(call.id, "Позиция удалена.")
            text, markup = order_utils.get_cart_details_markup(db, call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=text,
                                  reply_markup=markup)
        except Exception as e:
            session.rollback()
            bot.answer_callback_query(call.id, "Ошибка при удалении позиции.")
        finally:
            session.close()

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
    def confirm_order_callback(call):
        try:
            session = db.Session()
            from database.models import Order
            cart = session.query(Order).filter_by(user_id=call.from_user.id, status='cart').first()
            if not cart:
                bot.answer_callback_query(call.id, "Корзина пуста.")
                return
            cart.status = 'new'
            session.commit()
            bot.answer_callback_query(call.id, "Заказ подтвержден!")
            bot.send_message(call.message.chat.id, "Ваш заказ подтвержден. Ожидайте его обработки.")
        except Exception as e:
            session.rollback()
            bot.answer_callback_query(call.id, "Ошибка при подтверждении заказа.")
        finally:
            session.close()

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main_menu")
    def back_to_main_menu_callback(call):
        from handlers import main_menu
        main_menu.send_main_menu(bot, call.message.chat.id)
