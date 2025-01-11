# Standard Library
import datetime

# Third party
from dateutil.relativedelta import relativedelta
from kapt_catalog.models import ActivityPeriod

# Local application / specific library imports
from .mapping import (
    CORRESPONDENCE_MONTH_DAYS,
    CORRESPONDENCE_WEEK_DAYS,
    correspondence_special_dates,
)
from kapt_apidae.management.commands.import_apidae_to_kapt_travel.utils import (
    get_dates_from_monthdays,
    get_dates_from_weekdays,
    get_periods_from_dates,
)
from kapt_apidae.models import (
    OPENING_PERIOD_DAY_CHOICES,
    OPENING_PERIOD_TYPE_CHOICES,
    DayOpeningChoices,
)


OFFSET_STORE_PERIOD = 2


class PeriodActivityUpdateMixin:
    def update_periods(self):
        """
        Translates Apidae opening data in single opening periods.
        To do this, the following algorithm is performed for each Apidae period:
            1. If the period type is "OUVERTURE_TOUS_LES_JOURS", then the script creates a single period from the Apidae period datetime start
               to the datetime end.
            2. If the period type is "OUVERTURE_SAUF", a list of Apidae opened days is computed. These days are translated into Python weekdays
               numbers. By using the [dtstart, dtend] Apidae period and this list of weekdays, each opened datetime is computed.
            3. If the period type is "OUVERTURE_SEMAINE", a list of Apidae opened days is computed. These days are translated into Python weekdays
               numbers. By using the [dtstart, dtend] Apidae period and this list of weekdays, each opened datetime is computed.
            4. If the period type is "OUVERTURE_MOIS", each datetime in the [dtstart, dtend] Apidae period is computed by using the weekday and the number
               of the day in the considered month. These information are determined from the Apidae notation: D_1ER_LUNDI, D_2EME_LUNDI, ...
            5. The exceptional closure days are then subtracted from the previously computed opening periods.
        """

        now = datetime.date.today()
        max_dtstart = now + relativedelta(years=OFFSET_STORE_PERIOD)
        year_ranges = range(now.year, max_dtstart.year + 1)

        # Delete all previous opening periods
        ActivityPeriod.objects.filter(activity=self.activity).delete()

        # First handles opening periods
        for apidae_opening in self.touristic_object.opening_periods.all():
            periods_to_save = list()

            if (
                apidae_opening.type
                == OPENING_PERIOD_TYPE_CHOICES.OUVERTURE_TOUS_LES_JOURS
            ):
                period = ActivityPeriod(
                    activity=self.activity,
                    start=apidae_opening.beginning,
                    end=apidae_opening.ending,
                    further_hourly_informations=apidae_opening.further_hourly_informations,
                )
                periods_to_save.append(period)

            elif apidae_opening.type == OPENING_PERIOD_TYPE_CHOICES.OUVERTURE_SAUF:
                closed_days = apidae_opening.daily_opening.all()
                opened_days = DayOpeningChoices.objects.exclude(pk__in=closed_days)

                # Get Python weekdays values from Apidae opened weekdays
                if (
                    len(opened_days) == 1
                    and opened_days[0].day == OPENING_PERIOD_DAY_CHOICES.TOUS
                ):
                    opened_weekdays = [0, 1, 2, 3, 4, 5, 6]
                else:
                    opened_weekdays = [
                        CORRESPONDENCE_WEEK_DAYS[day.day] for day in opened_days
                    ]

                # Get the corresponding datetime objects
                opened_dates = get_dates_from_weekdays(
                    opened_weekdays, apidae_opening.beginning, apidae_opening.ending
                )

                # If the period is repeated every year
                if apidae_opening.every_years:
                    while apidae_opening.ending <= max_dtstart:
                        apidae_opening.ending = apidae_opening.ending + relativedelta(
                            years=1
                        )
                        apidae_opening.beginning = (
                            apidae_opening.beginning + relativedelta(years=1)
                        )
                        opened_dates += get_dates_from_weekdays(
                            opened_weekdays,
                            apidae_opening.beginning,
                            apidae_opening.ending,
                        )

                opened_periods = get_periods_from_dates(opened_dates)
                for period in opened_periods:
                    periods_to_save.append(
                        self._gen_activity_period(
                            self.activity, period[0], period[1], apidae_opening
                        )
                    )

            elif apidae_opening.type == OPENING_PERIOD_TYPE_CHOICES.OUVERTURE_SEMAINE:
                opened_days = apidae_opening.daily_opening.all()

                # Get Python weekdays values from Apidae opened weekdays
                if (
                    len(opened_days) == 1
                    and opened_days[0].day == OPENING_PERIOD_DAY_CHOICES.TOUS
                ):
                    opened_weekdays = [0, 1, 2, 3, 4, 5, 6]
                else:
                    opened_weekdays = [
                        CORRESPONDENCE_WEEK_DAYS[day.day] for day in opened_days
                    ]

                # Get the corresponding datetime objects
                opened_dates = get_dates_from_weekdays(
                    opened_weekdays, apidae_opening.beginning, apidae_opening.ending
                )

                # If the period is repeated every year
                if apidae_opening.every_years:
                    while apidae_opening.ending <= max_dtstart:
                        apidae_opening.ending = apidae_opening.ending + relativedelta(
                            years=1
                        )
                        apidae_opening.beginning = (
                            apidae_opening.beginning + relativedelta(years=1)
                        )
                        opened_dates += get_dates_from_weekdays(
                            opened_weekdays,
                            apidae_opening.beginning,
                            apidae_opening.ending,
                        )

                opened_periods = get_periods_from_dates(opened_dates)
                for period in opened_periods:
                    periods_to_save.append(
                        self._gen_activity_period(
                            self.activity, period[0], period[1], apidae_opening
                        )
                    )

            if apidae_opening.type == OPENING_PERIOD_TYPE_CHOICES.OUVERTURE_MOIS:
                opened_monthdays = list()

                for day in apidae_opening.monthly_opening.all():
                    opened_monthdays.append(CORRESPONDENCE_MONTH_DAYS[day.monthday])
                opened_dates = get_dates_from_monthdays(
                    opened_monthdays, apidae_opening.beginning, apidae_opening.ending
                )

                # If the period is repeated every year
                if apidae_opening.every_years:
                    while apidae_opening.ending <= max_dtstart:
                        apidae_opening.ending = apidae_opening.ending + relativedelta(
                            years=1
                        )
                        apidae_opening.beginning = (
                            apidae_opening.beginning + relativedelta(years=1)
                        )
                        opened_dates += get_dates_from_monthdays(
                            opened_monthdays,
                            apidae_opening.beginning,
                            apidae_opening.ending,
                        )

                opened_periods = get_periods_from_dates(opened_dates)
                for period in opened_periods:
                    periods_to_save.append(
                        self._gen_activity_period(
                            self.activity, period[0], period[1], apidae_opening
                        )
                    )

            # Last part: add exceptional opening to the periods to save
            for op in apidae_opening.exceptional_opening.all():
                date = op.date
                periods_to_save.append(
                    ActivityPeriod(activity=self.activity, start=date, end=date)
                )

            # Handle the case where the Apidae period is defined as recurrent
            every_years_periods_to_save = []
            if (
                apidae_opening.every_years
                and apidae_opening.type
                == OPENING_PERIOD_TYPE_CHOICES.OUVERTURE_TOUS_LES_JOURS
            ):
                for p in periods_to_save:
                    tmp_period = ActivityPeriod(
                        activity=p.activity, start=p.start, end=p.end
                    )
                    tmp_period.start = tmp_period.start + relativedelta(years=1)
                    tmp_period.end = tmp_period.end + relativedelta(years=1)
                    current_dtstart = tmp_period.start
                    current_dtend = tmp_period.end
                    while current_dtstart <= max_dtstart:
                        # Prepare the next iteration
                        tmp_period = ActivityPeriod(
                            activity=p.activity,
                            start=current_dtstart,
                            end=current_dtend,
                        )
                        every_years_periods_to_save.append(tmp_period)
                        current_dtstart = current_dtstart + relativedelta(years=1)
                        current_dtend = current_dtend + relativedelta(years=1)

            periods_to_save.extend(every_years_periods_to_save)
            # Save each computed period
            for p in periods_to_save:
                if p.start <= max_dtstart:
                    p.save()

        # Then handles exceptional closure dates
        for closure_period in self.touristic_object.exceptional_closure_dates.all():
            if closure_period.closure_date:
                start = end = closure_period.closure_date
                # Insert the corresponding closure period
                self.activity.insert_closure_period(start, end)
            elif closure_period.closure_special_date:
                for year in year_ranges:
                    closure_day = correspondence_special_dates(
                        closure_period.closure_special_date, year
                    )
                    if closure_day < max_dtstart:
                        # Insert the corresponding closure period
                        self.activity.insert_closure_period(closure_day, closure_day)

    def _gen_activity_period(self, activity, start, end, apidae_opening):
        activity_period = ActivityPeriod(
            activity=activity,
            start=start,
            end=end,
            further_hourly_informations=apidae_opening.further_hourly_informations,
        )
        if apidae_opening.opening_time and apidae_opening.closing_time:
            activity_period.opening_time = apidae_opening.opening_time
            activity_period.closing_time = apidae_opening.closing_time
        elif apidae_opening.opening_time:
            activity_period.opening_time = apidae_opening.opening_time
        return activity_period
