import os
import re
import csv

from django.conf import settings

from django.db.models import Max, Count
from django.core.management.base import BaseCommand
from stats.models import County, AgeGroupPop, CountyTestDate, StatewideAgeDate, StatewideTotalDate, Death


class Command(BaseCommand):
    help = 'Dump a CSV of the latest cumulative count of statewide and county-by-county data.'

    def dump_county_latest(self):
        with open(os.path.join(settings.BASE_DIR, 'exports', 'mn_covid_data', 'mn_positive_tests_by_county.csv'), 'w') as csvfile:

            fieldnames = ['county_fips', 'county_name', 'total_positive_tests', 'total_deaths', 'latitude', 'longitude']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            msg_output = '*Latest numbers from MPH:*\n\n'

            updated_total = 0

            for c in County.objects.all().order_by('name'):
                latest_observation = CountyTestDate.objects.filter(county=c).order_by('-scrape_date').first()
                if latest_observation:

                    updated_total += latest_observation.cumulative_count

                    row = {
                        'county_fips': c.fips,
                        'county_name': c.name,
                        'total_positive_tests': latest_observation.cumulative_count,
                        'total_deaths': latest_observation.cumulative_deaths,
                        'latitude': c.latitude,
                        'longitude': c.longitude,
                    }

                    writer.writerow(row)

    def dump_state_latest(self):
        with open(os.path.join(settings.BASE_DIR, 'exports', 'mn_covid_data', 'mn_statewide_latest.csv'), 'w') as csvfile:
            fieldnames = [
                'total_positive_tests',
                'daily_positive_tests',
                'daily_removed_tests',
                'total_statewide_deaths',
                'daily_statewide_deaths',
                'total_statewide_recoveries',
                'total_completed_tests',
                'total_completed_mdh',
                'total_completed_private',
                'total_hospitalized',
                'currently_hospitalized',
                'currently_in_icu',
                'last_update',
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            latest = StatewideTotalDate.objects.all().order_by('-last_update').first()
            writer.writerow({
                'total_positive_tests': latest.cumulative_positive_tests,
                'daily_positive_tests': latest.new_cases,
                'daily_removed_tests': latest.removed_cases,
                'total_statewide_deaths': latest.cumulative_statewide_deaths,
                'daily_statewide_deaths': latest.new_deaths,
                'total_statewide_recoveries': latest.cumulative_statewide_recoveries,
                'total_completed_tests': latest.cumulative_completed_tests,
                'total_completed_mdh': latest.cumulative_completed_mdh,
                'total_completed_private': latest.cumulative_completed_private,
                'total_hospitalized': latest.cumulative_hospitalized,
                'currently_hospitalized': latest.currently_hospitalized,
                'currently_in_icu': latest.currently_in_icu,
                'last_update': latest.last_update
            })

    def dump_ages_latest(self):
        with open(os.path.join(settings.BASE_DIR, 'exports', 'mn_covid_data', 'mn_ages_latest.csv'), 'w') as csvfile:

            fieldnames = [
                'age_group',
                'pct_of_cases',
                'pct_of_deaths',
                'pct_state_pop'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            max_date = StatewideAgeDate.objects.aggregate(Max('scrape_date'))['scrape_date__max']

            age_groups = AgeGroupPop.objects.all().order_by('pk')
            for a in age_groups:
                # print(a.age_group)
                    # print(s.age_group)
                lr = StatewideAgeDate.objects.get(age_group=a.age_group, scrape_date=max_date)
            # for lr in latest_records:
                writer.writerow({
                    'age_group': lr.age_group,
                    'pct_of_cases': lr.cases_pct,
                    'pct_of_deaths': lr.deaths_pct,
                    'pct_state_pop': a.pct_pop
                })

            missing = StatewideAgeDate.objects.get(age_group='Unknown/missing', scrape_date=max_date)
            writer.writerow({
                'age_group': missing.age_group,
                'pct_of_cases': missing.cases_pct,
                'pct_of_deaths': missing.deaths_pct,
                'pct_state_pop': 'N/A'
            })

    def dump_detailed_death_ages_latest(self):
        with open(os.path.join(settings.BASE_DIR, 'exports', 'mn_covid_data', 'mn_death_ages_detailed_latest.csv'), 'w') as csvfile:

            fieldnames = [
                'age_group',
                'num_deaths',
                'pct_of_deaths',
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            total_deaths = Death.objects.all().count()
            age_group_totals = Death.objects.all().values('age_group').annotate(total=Count('pk')).order_by('age_group')
            # print(age_group_totals)

            for ag in age_group_totals:
                ag['age_start_int'] = int(re.match(r'([0-9]+)', ag['age_group']).group(0))

            for ag in sorted(age_group_totals, key = lambda i: i['age_start_int']):
                # print(ag['age_start_int'])
                writer.writerow({
                    'age_group': ag['age_group'],
                    'num_deaths': ag['total'],
                    'pct_of_deaths': ag['total'] / total_deaths,
                })

    def handle(self, *args, **options):
        self.dump_county_latest()
        self.dump_state_latest()
        self.dump_ages_latest()
        self.dump_detailed_death_ages_latest()
