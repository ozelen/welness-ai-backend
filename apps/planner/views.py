from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date, timedelta

@login_required
def calendar_view(request):
	user = request.user
	week_param = request.GET.get('week')
	if week_param:
		try:
			year, week = map(int, week_param.split('-'))
			start_date = date.fromisocalendar(year, week, 1)
		except Exception:
			start_date = timezone.now().date()
	else:
		start_date = timezone.now().date()
	
	week_start = start_date - timedelta(days=start_date.weekday())
	week_days = [week_start + timedelta(days=i) for i in range(7)]
	week_end = week_days[-1]
	
	# Placeholder containers; integration with meals/activities will populate these
	events_by_day = {d: [] for d in week_days}
	
	context = {
		'week_start': week_start,
		'week_end': week_end,
		'week_days': week_days,
		'events_by_day': events_by_day,
	}
	return render(request, 'planner/calendar.html', context)
