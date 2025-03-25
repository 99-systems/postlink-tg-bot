import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from .schemas import DialogCalendarCallback, DialogCalAct, highlight, superscript
from .common import GenericCalendar


import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from .schemas import DialogCalendarCallback, DialogCalAct, highlight, superscript
from .common import GenericCalendar


# Modified DialogCalendar that only shows months from current onward and days
class DialogCalendar(GenericCalendar):
    ignore_callback = DialogCalendarCallback(act=DialogCalAct.ignore).pack()  # placeholder for no answer buttons

    async def _get_month_kb(self):
        """Creates an inline keyboard with months from current month forward"""
        today = datetime.now()
        current_month, current_year = today.month, today.year
        
        kb = []
        
        # Only include months from current month forward
        months_to_show = range(current_month, 13)
        
        # Create rows with months (up to 3 months per row)
        month_row = []
        for i, month in enumerate(months_to_show):
            month_str = self._labels.months[month - 1]
            if current_month == month:
                month_str = highlight(month_str)
                
            month_row.append(InlineKeyboardButton(
                text=month_str,
                callback_data=DialogCalendarCallback(
                    act=DialogCalAct.set_m, year=current_year, month=month, day=-1
                ).pack()
            ))
            
            # Create a new row after every 3 months
            if (i + 1) % 3 == 0 or month == months_to_show[-1]:
                kb.append(month_row)
                month_row = []
        
        return InlineKeyboardMarkup(row_width=3, inline_keyboard=kb)

    async def _get_days_kb(self, month: int):
        """Creates an inline keyboard with calendar days of month"""
        today = datetime.now()
        current_year = today.year
        now_weekday = self._labels.days_of_week[today.weekday()]
        now_month, now_day = today.month, today.day

        def highlight_weekday():
            if now_month == month and now_weekday == weekday:
                return highlight(weekday)
            return weekday

        def format_day_string():
            date_to_check = datetime(current_year, month, day)
            
            # Check if date is in allowed range
            if self.min_date and date_to_check < self.min_date:
                return superscript(str(day))
            elif self.max_date and date_to_check > self.max_date:
                return superscript(str(day))
                
            return str(day)

        def highlight_day():
            day_string = format_day_string()
            if now_month == month and now_day == day:
                return highlight(day_string)
            return day_string

        kb = []
        
        # Month header row
        month_str = self._labels.months[month - 1]
        if now_month == month:
            month_str = highlight(month_str)
            
        nav_row = []
        nav_row.append(InlineKeyboardButton(
            text=month_str,
            callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=current_year, month=-1, day=-1).pack()
        ))
        kb.append(nav_row)

        # Weekday labels row
        week_days_labels_row = []
        for weekday in self._labels.days_of_week:
            week_days_labels_row.append(InlineKeyboardButton(
                text=highlight_weekday(), callback_data=self.ignore_callback))
        kb.append(week_days_labels_row)

        # Calendar days
        month_calendar = calendar.monthcalendar(current_year, month)
        for week in month_calendar:
            days_row = []
            for day in week:
                if day == 0:
                    days_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
                    continue
                
                # For current month, disable past days
                if month == now_month and day < now_day:
                    days_row.append(InlineKeyboardButton(
                        text=superscript(str(day)),
                        callback_data=self.ignore_callback
                    ))
                else:
                    days_row.append(InlineKeyboardButton(
                        text=highlight_day(),
                        callback_data=DialogCalendarCallback(
                            act=DialogCalAct.day, year=current_year, month=month, day=day
                        ).pack()
                    ))
            kb.append(days_row)
            
        # Back to months button
        back_row = []
        back_row.append(InlineKeyboardButton(
            text="« Назад к месяцам",
            callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=current_year, month=-1, day=-1).pack()
        ))
        kb.append(back_row)
        
        return InlineKeyboardMarkup(row_width=7, inline_keyboard=kb)

    async def start_calendar(self) -> InlineKeyboardMarkup:
        """Start showing the calendar directly with the month selection"""
        return await self._get_month_kb()

    async def process_selection(self, query: CallbackQuery, data: DialogCalendarCallback) -> tuple:
        """Process the callback from calendar buttons"""
        return_data = (False, None)
        
        if data.act == DialogCalAct.ignore:
            await query.answer(cache_time=60)
        
        if data.act == DialogCalAct.start:
            await query.message.edit_reply_markup(reply_markup=await self._get_month_kb())
            
        if data.act == DialogCalAct.set_m:
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(int(data.month)))
            
        if data.act == DialogCalAct.day:
            return await self.process_day_select(data, query)

        return return_data