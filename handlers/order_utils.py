import logging

def get_current_cart(db, user_id):
    """
    Возвращает заказ со статусом 'cart' (корзина) для указанного пользователя.
    """
    session = db.Session()
    try:
        from database.models import Order
        cart = session.query(Order).filter_by(user_id=user_id, status='cart').first()
        return cart
    except Exception as e:
        logging.error("Ошибка при получении корзины для пользователя %s: %s", user_id, e)
        return None
    finally:
        session.close()

def get_cart_details(db, user_id):
    """
    Формирует текстовое описание текущей корзины пользователя.
    """
    from database.models import OrderItem  # Импортируем внутри функции
    cart = get_current_cart(db, user_id)
    if not cart:
        return "Ваша корзина пуста."

    session = db.Session()
    try:
        order_items = session.query(OrderItem).filter_by(order_id=cart.id).all()
        if not order_items:
            return "Ваша корзина пуста."
        message_lines = ["Ваш заказ:"]
        for item in order_items:
            dish = db.get_dish(item.dish_id)
            dish_name = dish.name if dish else "Блюдо"
            message_lines.append(f"{dish_name} — {item.quantity} шт. — {item.total} руб.")
        message_lines.append(f"Общая стоимость: {cart.total_cost} руб.")
        return "\n".join(message_lines)
    except Exception as e:
        logging.error("Ошибка при получении деталей корзины: %s", e)
        return "Ошибка при получении деталей заказа."
    finally:
        session.close()

def get_cart_details_markup(db, user_id):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    cart = get_current_cart(db, user_id)
    if not cart:
        return "Ваша корзина пуста.", None
    session = db.Session()
    try:
        from database.models import OrderItem, Dish
        order_items = session.query(OrderItem).filter_by(order_id=cart.id).all()
        if not order_items:
            return "Ваша корзина пуста.", None
        message_lines = ["Ваш заказ:"]
        markup = InlineKeyboardMarkup()
        for item in order_items:
            dish = db.get_dish(item.dish_id)
            dish_name = dish.name if dish else "Блюдо"
            message_lines.append(f"{dish_name} — {item.quantity} шт. — {item.total} руб.")
            # Клавиатура для изменения количества и удаления позиции
            row = [
                InlineKeyboardButton("➕", callback_data=f"increase_{item.id}"),
                InlineKeyboardButton("➖", callback_data=f"decrease_{item.id}"),
                InlineKeyboardButton("Удалить", callback_data=f"remove_{item.id}")
            ]
            markup.add(*row)
        message_lines.append(f"Общая стоимость: {cart.total_cost} руб.")
        # Кнопки для подтверждения заказа и возврата в главное меню
        markup.add(InlineKeyboardButton("Подтвердить заказ", callback_data="confirm_order"))
        markup.add(InlineKeyboardButton("Назад в главное меню", callback_data="back_to_main_menu"))
        return "\n".join(message_lines), markup
    except Exception as e:
        import logging
        logging.error("Ошибка при получении деталей корзины: %s", e)
        return "Ошибка при получении деталей заказа.", None
    finally:
        session.close()
