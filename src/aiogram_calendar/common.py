import calendar
import locale

from aiogram.types import User
from datetime import datetime

from .schemas import CalendarLabels


async def get_user_locale(from_user: User) -> str:
    """Returns user locale in format en_US, accepts User instance from Message, CallbackData etc"""
    # Safe locale mapping
    safe_locales = {
        "en": "en_US",
        "ru": "en_US",  # Use en_US as fallback if Russian isn't available
        "uk": "en_US",
        "de": "en_US",
        "fr": "en_US",
        "es": "en_US",
        # Add more mappings as needed
    }
    
    if from_user and hasattr(from_user, 'language_code') and from_user.language_code:
        # Get the base language code (first 2 characters)
        base_lang = from_user.language_code.split('-')[0][:2].lower()
        return safe_locales.get(base_lang, "en_US")
    
    return "en_US"  # Default fallback


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

        self.min_date = None
        self.max_date = None
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
                f'The date have to be later {self.min_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'The date have to be before {self.max_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        await query.message.delete_reply_markup()  # removing inline keyboard
        return True, date
