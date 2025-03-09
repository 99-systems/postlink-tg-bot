import calendar
from datetime import datetime

from aiogram.types import User

from .schemas import CalendarLabels


# GenericCalendar class implementation
class GenericCalendar:
    def __init__(
        self,
        locale: str = None,
        today_btn: str = None,
        show_alerts: bool = False
    ) -> None:
        """Pass labels if you need to have alternative language of buttons
        Parameters:
        locale (str): Locale calendar must have captions in (in format uk_UA), if None - default English will be used
        today_btn (str): label for button Today to set calendar back to todays date
        show_alerts (bool): defines how the date range error would shown (defaults to False)
        """
        self._labels = CalendarLabels()
        if locale:
            # getting month names and days of week in specified locale
            with calendar.different_locale(locale):
                self._labels.days_of_week = list(calendar.day_abbr)
                self._labels.months = calendar.month_abbr[1:]
        if today_btn:
            self._labels.today_caption = today_btn
        
        # Set default date range to current date and one year in the future
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        max_date = datetime(today.year + 1, today.month, today.day)
        self.min_date = today
        self.max_date = max_date
        self.show_alerts = show_alerts
    
    def set_dates_range(self, min_date: datetime, max_date: datetime):
        """Sets range of minimum & maximum dates"""
        self.min_date = min_date
        self.max_date = max_date
    
    async def process_day_select(self, data, query):
        """Checks selected date is in allowed range of dates"""
        date = datetime(int(data.year), int(data.month), int(data.day))
        
        if self.min_date and self.min_date > date:
            await query.answer(
                f'Date must not be earlier than {self.min_date.strftime("%d.%m.%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'Date must not be later than {self.max_date.strftime("%d.%m.%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        
        await query.message.delete_reply_markup()  # removing inline keyboard
        return True, date


# Valid locales handling
valid_locales = {"en_US.utf8", "C", "C.utf8", "POSIX"}

async def get_user_locale(from_user: User) -> str:
    """Returns a locale available on Heroku (en_US.utf8 by default)"""
    safe_locales = {
        "en": "en_US.utf8",
        "ru": "en_US.utf8",
        "uk": "en_US.utf8",
        "de": "en_US.utf8",
        "fr": "en_US.utf8",
        "es": "en_US.utf8",
    }
    
    if from_user and hasattr(from_user, "language_code") and from_user.language_code:
        lang_code = from_user.language_code.lower()
        locale_str = safe_locales.get(lang_code[:2], "en_US.utf8")
        if locale_str not in valid_locales:
            locale_str = "en_US.utf8"
        return locale_str
    return "en_US.utf8"


