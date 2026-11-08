# -*- coding: utf-8 -*-
"""
Калькулятор себестоимости установки окон
Версия 1.0.0
Соответствует ТЗ по IEEE Std 830-1998
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window

# ====================== СПРАВОЧНИКИ (встроенные данные) ======================

WINDOWS = {
    "ПВХ 2-створчатое": 25000.0,
    "ПВХ 3-створчатое": 35000.0,
    "Деревянное 2-створчатое": 20000.0,
    "Алюминиевое": 30000.0,
}

# Работа: (норма_времени_ч, стоимость_машин, {материал: норма_расхода})
WORKS = {
    "Демонтаж старого окна": (2.0, 30.0, {"Пена монтажная": 0.5}),
    "Монтаж окна ПВХ": (4.0, 60.0, {
        "Пена монтажная": 1.0,
        "Крепёж": 1.0,
        "Герметик": 0.5,
        "Лента пароизоляционная": 1.0
    }),
    "Монтаж деревянного окна": (4.5, 60.0, {
        "Пена монтажная": 1.0,
        "Крепёж": 1.0,
        "Герметик": 0.5,
        "Лента пароизоляционная": 1.0
    }),
    "Монтаж алюминиевого окна": (3.5, 50.0, {
        "Пена монтажная": 0.8,
        "Крепёж": 1.0,
        "Герметик": 0.5,
        "Лента пароизоляционная": 1.0
    }),
    "Установка подоконника": (0.5, 10.0, {"Подоконник": 1.0}),
    "Установка откосов": (0.7, 15.0, {"Откос": 1.0, "Герметик": 0.3}),
    "Установка отлива": (0.3, 5.0, {"Отлив": 1.0}),
    "Регулировка фурнитуры": (0.3, 0.0, {}),
}

MATERIALS = {
    "Пена монтажная": 350.0,
    "Крепёж": 120.0,
    "Герметик": 280.0,
    "Лента пароизоляционная": 90.0,
    "Подоконник": 1800.0,
    "Откос": 950.0,
    "Отлив": 650.0,
}

RATES = {
    "2 разряд": 280.0,
    "3 разряд": 320.0,
    "4 разряд": 370.0,
    "5 разряд": 410.0,
    "6 разряд": 450.0,
}

# ====================== УТИЛИТЫ ======================

def parse_float(text, default=None):
    try:
        return float(text.replace(",", ".").strip())
    except (ValueError, AttributeError):
        return default

def parse_int(text, default=None):
    try:
        return int(float(text.replace(",", ".").strip()))
    except (ValueError, AttributeError):
        return default

def money(value):
    """Форматирование денег: 1 234,56"""
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")

# ====================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ======================

class WindowCostCalculator(App):
    def build(self):
        self.title = "Калькулятор окон"
        Window.softinput_mode = "below_target"

        # Рабочие копии справочников (чтобы можно было редактировать цены)
        self.materials = MATERIALS.copy()
        self.rates = RATES.copy()

        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        # Заголовок
        root.add_widget(Label(
            text="[b]Калькулятор установки окон[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(36),
            font_size=dp(18)
        ))

        # Прокручиваемая область
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        root.add_widget(scroll)

        self._build_content(content)
        return root

    def _build_content(self, content):
        # ---------- 1. Параметры окна ----------
        content.add_widget(Label(text="[b]1. Параметры окна[/b]", markup=True,
                                 size_hint_y=None, height=dp(28)))

        row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        row.add_widget(Label(text="Тип окна:", size_hint_x=0.35))
        self.window_spinner = Spinner(
            text="ПВХ 2-створчатое",
            values=list(WINDOWS.keys()),
            size_hint_x=0.65
        )
        row.add_widget(self.window_spinner)
        content.add_widget(row)

        row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        row.add_widget(Label(text="Количество окон:", size_hint_x=0.55))
        self.qty_input = TextInput(
            text="1",
            input_filter="int",
            multiline=False,
            size_hint_x=0.45
        )
        row.add_widget(self.qty_input)
        content.add_widget(row)

        row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        self.include_window_cost = CheckBox(size_hint_x=None, width=dp(32))
        row.add_widget(self.include_window_cost)
        row.add_widget(Label(text="Включить стоимость окна в итог", size_hint_x=1))
        content.add_widget(row)

        # ---------- 2. Опции ----------
        content.add_widget(Label(text="[b]2. Опции установки[/b]", markup=True,
                                 size_hint_y=None, height=dp(28)))

        btn_std = Button(
            text="Стандартный набор (демонтаж + монтаж + добор)",
            size_hint_y=None,
            height=dp(42),
            background_color=(0.2, 0.5, 0.8, 1)
        )
        btn_std.bind(on_press=self._check_standard)
        content.add_widget(btn_std)

        # Заголовок таблицы опций
        header = BoxLayout(size_hint_y=None, height=dp(30))
        header.add_widget(Label(text="✓", size_hint_x=0.12))
        header.add_widget(Label(text="Работа", size_hint_x=0.58))
        header.add_widget(Label(text="Кол-во", size_hint_x=0.30))
        content.add_widget(header)

        self.option_rows = []
        for name in WORKS.keys():
            row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(4))
            cb = CheckBox(size_hint_x=0.12)
            lbl = Label(text=name, size_hint_x=0.58, shorten=True, shorten_from="right")
            qty = TextInput(text="1", input_filter="int", multiline=False, size_hint_x=0.30)
            row.add_widget(cb)
            row.add_widget(lbl)
            row.add_widget(qty)
            content.add_widget(row)
            self.option_rows.append({"name": name, "cb": cb, "qty": qty})

        # ---------- 3. Тарификация ----------
        content.add_widget(Label(text="[b]3. Тарификация и накладные[/b]", markup=True,
                                 size_hint_y=None, height=dp(28)))

        row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        row.add_widget(Label(text="Разряд:", size_hint_x=0.35))
        self.rate_spinner = Spinner(
            text="4 разряд",
            values=list(RATES.keys()),
            size_hint_x=0.65
        )
        row.add_widget(self.rate_spinner)
        content.add_widget(row)

        row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        row.add_widget(Label(text="Накладные, %:", size_hint_x=0.55))
        self.overhead_input = TextInput(
            text="20",
            input_filter="float",
            multiline=False,
            size_hint_x=0.45
        )
        row.add_widget(self.overhead_input)
        content.add_widget(row)

        # ---------- Кнопки ----------
        btn_calc = Button(
            text="РАССЧИТАТЬ",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.15, 0.65, 0.25, 1),
            font_size=dp(16)
        )
        btn_calc.bind(on_press=self._calculate)
        content.add_widget(btn_calc)

        btn_edit = Button(
            text="Редактировать цены",
            size_hint_y=None,
            height=dp(42),
            background_color=(0.85, 0.45, 0.1, 1)
        )
        btn_edit.bind(on_press=self._open_price_editor)
        content.add_widget(btn_edit)

        # ---------- Результат ----------
        content.add_widget(Label(text="[b]4. Результат[/b]", markup=True,
                                 size_hint_y=None, height=dp(28)))

        self.result_label = Label(
            text="Нажмите «Рассчитать»",
            markup=True,
            size_hint_y=None,
            text_size=(None, None),
            halign="left",
            valign="top"
        )
        self.result_label.bind(
            texture_size=lambda instance, size: setattr(instance, "height", max(size[1], dp(80)))
        )
        content.add_widget(self.result_label)

    # ====================== ЛОГИКА ======================

    def _check_standard(self, instance):
        """Стандартный набор опций"""
        window = self.window_spinner.text
        if "ПВХ" in window:
            montage = "Монтаж окна ПВХ"
        elif "Деревянн" in window:
            montage = "Монтаж деревянного окна"
        else:
            montage = "Монтаж алюминиевого окна"

        standard = {
            "Демонтаж старого окна",
            montage,
            "Установка подоконника",
            "Установка откосов",
            "Установка отлива",
            "Регулировка фурнитуры"
        }

        for row in self.option_rows:
            row["cb"].active = row["name"] in standard
            row["qty"].text = "1"

    def _show_error(self, message):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(Label(text=message, text_size=(dp(280), None)))
        btn = Button(text="OK", size_hint_y=None, height=dp(40))
        content.add_widget(btn)

        popup = Popup(
            title="Ошибка",
            content=content,
            size_hint=(0.85, 0.35),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def _calculate(self, instance):
        # Проверка количества окон
        qty_windows = parse_int(self.qty_input.text)
        if qty_windows is None or qty_windows <= 0:
            self._show_error("Количество окон должно быть целым положительным числом.")
            return

        # Проверка накладных
        overhead_pct = parse_float(self.overhead_input.text)
        if overhead_pct is None:
            self._show_error("Накладные расходы должны быть числом.")
            return

        # Собираем выбранные опции
        selected = []
        for row in self.option_rows:
            if row["cb"].active:
                q = parse_int(row["qty"].text, default=1)
                if q is None or q <= 0:
                    q = 1
                selected.append((row["name"], q))

        if not selected:
            self._show_error("Выберите хотя бы одну опцию.")
            return

        rate = self.rates[self.rate_spinner.text]
        window_price = WINDOWS[self.window_spinner.text]

        # Расчёт
        total_zp = 0.0
        total_machines = 0.0
        total_materials = 0.0
        detail_lines = []

        for name, qty in selected:
            time_norm, machine_cost, mats = WORKS[name]

            zp = time_norm * rate * qty
            machines = machine_cost * qty

            mat_cost = 0.0
            mat_detail = []
            for mat_name, norm in mats.items():
                price = self.materials.get(mat_name, 0.0)
                cost = norm * price * qty
                mat_cost += cost
                mat_detail.append(f"    • {mat_name}: {money(cost)} руб.")

            direct = zp + machines + mat_cost

            total_zp += zp
            total_machines += machines
            total_materials += mat_cost

            detail_lines.append(
                f"[b]{name}[/b] × {qty}\n"
                f"  ЗП: {money(zp)}  |  Машины: {money(machines)}\n"
                f"  Материалы: {money(mat_cost)}\n" +
                ("\n".join(mat_detail) + "\n" if mat_detail else "") +
                f"  Прямые: {money(direct)}\n"
            )

        direct_total = total_zp + total_machines + total_materials
        overhead = direct_total * overhead_pct / 100.0
        works_total = direct_total + overhead

        windows_cost = 0.0
        if self.include_window_cost.active:
            windows_cost = window_price * qty_windows

        grand_total = works_total + windows_cost
        per_window = grand_total / qty_windows

        # Формирование текста результата
        text = "[b]ДЕТАЛИЗАЦИЯ[/b]\n\n" + "\n".join(detail_lines)
        text += "\n[b]СВОДКА[/b]\n"
        text += f"Зарплата рабочих:     {money(total_zp)} руб.\n"
        text += f"Машины и механизмы:   {money(total_machines)} руб.\n"
        text += f"Материалы:            {money(total_materials)} руб.\n"
        text += f"Прямые затраты:       {money(direct_total)} руб.\n"
        text += f"Накладные ({overhead_pct:.0f}%):  {money(overhead)} руб.\n"
        text += f"Итого работы:         {money(works_total)} руб.\n"
        if windows_cost > 0:
            text += f"Стоимость окон:       {money(windows_cost)} руб.\n"
        text += f"\n[b]ВСЕГО: {money(grand_total)} руб.[/b]\n"
        text += f"На 1 окно:            {money(per_window)} руб."

        self.result_label.text = text

    def _open_price_editor(self, instance):
        layout = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, padding=dp(8))
        layout.bind(minimum_height=layout.setter("height"))

        inputs = {}

        # Материалы
        layout.add_widget(Label(text="[b]Материалы[/b]", markup=True, size_hint_y=None, height=dp(30)))
        layout.add_widget(Label(text="", size_hint_y=None, height=dp(30)))

        for name, price in self.materials.items():
            layout.add_widget(Label(text=name, size_hint_y=None, height=dp(36), shorten=True))
            ti = TextInput(text=str(price), multiline=False, size_hint_y=None, height=dp(36))
            layout.add_widget(ti)
            inputs[("mat", name)] = ti

        # Ставки
        layout.add_widget(Label(text="[b]Часовые ставки[/b]", markup=True, size_hint_y=None, height=dp(30)))
        layout.add_widget(Label(text="", size_hint_y=None, height=dp(30)))

        for name, rate in self.rates.items():
            layout.add_widget(Label(text=name, size_hint_y=None, height=dp(36)))
            ti = TextInput(text=str(rate), multiline=False, size_hint_y=None, height=dp(36))
            layout.add_widget(ti)
            inputs[("rate", name)] = ti

        scroll = ScrollView(size_hint=(1, 0.85))
        scroll.add_widget(layout)

        btn_box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10), padding=dp(6))
        btn_save = Button(text="Сохранить", background_color=(0.2, 0.6, 0.2, 1))
        btn_cancel = Button(text="Отмена")
        btn_box.add_widget(btn_save)
        btn_box.add_widget(btn_cancel)

        content = BoxLayout(orientation="vertical")
        content.add_widget(scroll)
        content.add_widget(btn_box)

        popup = Popup(
            title="Редактирование цен",
            content=content,
            size_hint=(0.96, 0.96),
            auto_dismiss=False
        )

        def save(instance):
            for key, ti in inputs.items():
                val = parse_float(ti.text)
                if val is not None and val >= 0:
                    kind, name = key
                    if kind == "mat":
                        self.materials[name] = val
                    else:
                        self.rates[name] = val
            popup.dismiss()

        btn_save.bind(on_press=save)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

# ====================== ЗАПУСК ======================

if __name__ == "__main__":
    WindowCostCalculator().run()
